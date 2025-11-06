#!/usr/bin/env python3
"""
Enhanced Scare Script with Recording
Displays a static image, plays a scary video when motion is detected,
and records the person's reaction for playback.

Usage: python3 scare2.py [VideoName]
Example: python3 scare2.py Female
"""

import subprocess as sp
import time
import os
import sys
import logging
import datetime
from pathlib import Path
from typing import Optional
import yaml

from pirdetect import Detector


class ScareSystemWithRecording:
    """Enhanced scare system with reaction recording capability."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the scare system with recording.

        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.video_name: Optional[str] = None
        self.detector: Optional[Detector] = None

    def load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"WARNING: Config file '{config_path}' not found. Using defaults.")
            return self.get_default_config()
        except yaml.YAMLError as e:
            print(f"ERROR: Failed to parse config file: {e}")
            sys.exit(1)

    def get_default_config(self) -> dict:
        """Return default configuration if config file is missing."""
        return {
            'gpio': {'sensor_pin': 7, 'pin_mode': 'BOARD', 'pull_mode': 'DOWN'},
            'paths': {
                'media_dir': '/home/pi/Projects/Halloween/ScareMedia',
                'recordings_dir': '/home/pi/Projects/Halloween/Recordings'
            },
            'video': {
                'player': 'omxplayer',
                'output': 'both',
                'resolution': {'width': 1280, 'height': 720},
                'aspect_mode': 'fill',
                'orientation': 180,
                'volume': -600,
                'show_osd': False
            },
            'camera': {
                'duration': 5000,
                'rotation': 180,
                'preview': False
            },
            'display': {'device': '/dev/fb0', 'terminal': 1},
            'motion': {'poll_interval': 0.1},
            'logging': {'enabled': True, 'level': 'INFO', 'console_output': True},
            'themes': {
                'file_format': {
                    'video_suffix': 'ScareV.mp4',
                    'image_suffix': 'Start.png'
                }
            }
        }

    def setup_logging(self):
        """Configure logging based on config settings."""
        log_config = self.config.get('logging', {})

        if not log_config.get('enabled', True):
            logging.disable(logging.CRITICAL)
            return

        level = getattr(logging, log_config.get('level', 'INFO'))
        handlers = []

        if log_config.get('console_output', True):
            handlers.append(logging.StreamHandler())

        if 'log_file' in log_config:
            try:
                handlers.append(logging.FileHandler(log_config['log_file']))
            except Exception as e:
                print(f"WARNING: Could not create log file: {e}")

        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )

    def ensure_recordings_dir(self):
        """Ensure recordings directory exists."""
        try:
            recordings_dir = Path(self.config['paths']['recordings_dir'])
            recordings_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Recordings directory ready: {recordings_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create recordings directory: {e}")
            raise

    def get_recording_filename(self) -> str:
        """
        Generate timestamped filename for recording.

        Returns:
            Full path to recording file
        """
        recordings_dir = self.config['paths']['recordings_dir']
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        return f"{recordings_dir}/{timestamp}.h264"

    def get_video_command(self, video_path: str) -> list:
        """Build video playback command from config."""
        video_cfg = self.config['video']
        res = video_cfg['resolution']

        cmd = [
            video_cfg['player'],
            video_path,
            "-o", video_cfg['output'],
            "--win", f"0 0 {res['width']} {res['height']}",
            "--aspect-mode", video_cfg['aspect_mode'],
            "--orientation", str(video_cfg['orientation']),
            "--vol", str(video_cfg['volume'])
        ]

        if not video_cfg.get('show_osd', False):
            cmd.append("--no-osd")

        return cmd

    def get_record_command(self, output_file: str) -> list:
        """
        Build camera recording command from config.

        Args:
            output_file: Path to save recording

        Returns:
            Command list for subprocess
        """
        camera_cfg = self.config['camera']

        cmd = [
            "raspivid",
            "-o", output_file,
            "-t", str(camera_cfg['duration']),
            "-rot", str(camera_cfg['rotation'])
        ]

        if not camera_cfg.get('preview', False):
            cmd.append("-n")

        return cmd

    def subprocess_wait(self, params: list) -> bool:
        """
        Execute subprocess and wait for completion.

        Args:
            params: Command parameters

        Returns:
            True if successful, False otherwise
        """
        try:
            sub = sp.Popen(params)
            while sub.poll() is None:
                time.sleep(0.1)
            return sub.returncode == 0
        except Exception as e:
            self.logger.error(f"Subprocess error: {e}")
            return False

    def show_image(self, video_name: str):
        """Display static start image on framebuffer."""
        try:
            media_dir = self.config['paths']['media_dir']
            image_suffix = self.config['themes']['file_format']['image_suffix']
            display_cfg = self.config['display']

            image_path = f"{media_dir}/{video_name}{image_suffix}"
            cmd = (
                f"sudo fbi -T {display_cfg['terminal']} "
                f"-d {display_cfg['device']} -noverbose -once {image_path}"
            )

            self.logger.info(f"Displaying image: {image_path}")
            os.system(cmd)
        except Exception as e:
            self.logger.error(f"Failed to display image: {e}")

    def on_motion(self, curr_state: bool):
        """
        Callback function triggered on motion detection.
        Records reaction while playing scary video, then plays back recording.

        Args:
            curr_state: Current motion sensor state
        """
        if not curr_state:
            return

        try:
            # Get file paths
            media_dir = self.config['paths']['media_dir']
            video_suffix = self.config['themes']['file_format']['video_suffix']
            scare_file = f"{media_dir}/{self.video_name}{video_suffix}"
            recording_file = self.get_recording_filename()

            self.logger.info(f"Motion detected! Starting scare sequence")
            self.logger.info(f"Recording to: {recording_file}")

            # Start recording (runs in background)
            record_cmd = self.get_record_command(recording_file)
            self.logger.debug(f"Record command: {' '.join(record_cmd)}")
            sub_record = sp.Popen(record_cmd)

            # Play scary video (wait for completion)
            self.logger.info(f"Playing scary video: {scare_file}")
            video_cmd = self.get_video_command(scare_file)
            self.subprocess_wait(video_cmd)

            # Wait for recording to finish (if still running)
            if sub_record.poll() is None:
                self.logger.info("Waiting for recording to complete...")
                sub_record.wait()

            # Play back the recording
            if Path(recording_file).exists():
                self.logger.info(f"Playing back recording: {recording_file}")
                playback_cmd = self.get_video_command(recording_file)
                self.subprocess_wait(playback_cmd)
            else:
                self.logger.warning("Recording file not found, skipping playback")

            self.logger.info("Scare sequence completed")

        except Exception as e:
            self.logger.error(f"Error during scare sequence: {e}")

    def cleanup(self):
        """Clean up resources and restore display."""
        try:
            self.logger.info("Cleaning up...")
            os.system("sudo killall -9 fbi")
            if self.detector:
                self.detector.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def run(self, video_name: str):
        """
        Start the scare system with recording.

        Args:
            video_name: Name of the video theme to use
        """
        self.video_name = video_name

        # Ensure recordings directory exists
        self.ensure_recordings_dir()

        # Show initial image
        self.show_image(video_name)

        # Initialize motion detector
        gpio_cfg = self.config['gpio']
        self.detector = Detector(
            sensor_pin=gpio_cfg['sensor_pin'],
            pin_mode=gpio_cfg['pin_mode'],
            pull_mode=gpio_cfg['pull_mode']
        )

        # Subscribe to motion events
        self.detector.subscribe(self.on_motion)

        # Start detection loop
        try:
            poll_interval = self.config['motion']['poll_interval']
            self.detector.start(poll_interval=poll_interval)
        except KeyboardInterrupt:
            self.logger.info("Stopped by user")
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 scare2.py [VideoName]")
        print("Example: python3 scare2.py Female")
        sys.exit(1)

    video_name = sys.argv[1]

    try:
        scare = ScareSystemWithRecording()
        scare.run(video_name)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
