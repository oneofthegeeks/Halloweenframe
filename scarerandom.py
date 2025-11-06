#!/usr/bin/env python3
"""
Advanced Scare Script with Random Video Rotation
Rotates through multiple scary videos at configurable intervals,
records reactions, and plays them back.

Usage: python3 scarerandom.py [VideoName] [Minutes]
Example: python3 scarerandom.py Male 10

This script will:
1. Start with the specified video theme
2. Rotate to a random different theme every N minutes
3. Record reactions for each scare
4. Never play the same video twice in a row
"""

import subprocess as sp
import time
import os
import sys
import logging
import datetime
import random
from pathlib import Path
from typing import Optional, List
import yaml

from pirdetect import Detector


class AdvancedScareSystem:
    """Advanced scare system with video rotation and reaction recording."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the advanced scare system.

        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        # Video rotation state
        self.current_prefix: str = ""
        self.new_prefix: str = ""
        self.scare_file: str = ""
        self.start_time: float = time.time()
        self.rotation_minutes: int = 0

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
            'themes': {
                'available': ['Male', 'Female', 'Child'],
                'file_format': {
                    'video_suffix': 'ScareV.mp4',
                    'image_suffix': 'Start.png'
                }
            },
            'display': {'device': '/dev/fb0', 'terminal': 1},
            'motion': {'poll_interval': 0.1},
            'logging': {'enabled': True, 'level': 'INFO', 'console_output': True}
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

    def get_available_themes(self) -> List[str]:
        """Get list of available video themes from config."""
        return self.config['themes']['available']

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
        """Generate timestamped filename for recording."""
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
        """Build camera recording command from config."""
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
        """Execute subprocess and wait for completion."""
        try:
            sub = sp.Popen(params)
            while sub.poll() is None:
                time.sleep(0.1)
            return sub.returncode == 0
        except Exception as e:
            self.logger.error(f"Subprocess error: {e}")
            return False

    def show_image(self, theme_name: str):
        """Display static start image on framebuffer."""
        try:
            media_dir = self.config['paths']['media_dir']
            image_suffix = self.config['themes']['file_format']['image_suffix']
            display_cfg = self.config['display']

            image_path = f"{media_dir}/{theme_name}{image_suffix}"
            cmd = (
                f"sudo fbi -T {display_cfg['terminal']} "
                f"-d {display_cfg['device']} -noverbose -once {image_path}"
            )

            self.logger.info(f"Displaying image: {image_path}")
            os.system(cmd)
        except Exception as e:
            self.logger.error(f"Failed to display image: {e}")

    def change_video(self):
        """
        Check if it's time to rotate to a new video and do so if needed.
        Ensures the new video is different from the current one.
        """
        elapsed_time = time.time() - self.start_time
        elapsed_delta = datetime.timedelta(seconds=elapsed_time)

        self.logger.info(f"Time since last rotation: {elapsed_delta}")

        if elapsed_time > (self.rotation_minutes * 60):
            video_themes = self.get_available_themes()

            # Select a new random video (different from current)
            attempts = 0
            while self.new_prefix == self.current_prefix and attempts < 10:
                self.new_prefix = random.choice(video_themes)
                attempts += 1

            if attempts >= 10:
                self.logger.warning("Could not find different video, keeping current")
                return

            self.current_prefix = self.new_prefix
            media_dir = self.config['paths']['media_dir']
            video_suffix = self.config['themes']['file_format']['video_suffix']
            self.scare_file = f"{media_dir}/{self.current_prefix}{video_suffix}"

            self.start_time = time.time()
            self.show_image(self.current_prefix)

            self.logger.info(f"Updating video to: {self.current_prefix}")
            print(f"\n** Video rotated to: {self.current_prefix} **\n")

    def on_motion(self, curr_state: bool):
        """
        Callback function triggered on motion detection.
        Records reaction while playing scary video, then plays back recording.
        Also checks if it's time to rotate videos.

        Args:
            curr_state: Current motion sensor state
        """
        if not curr_state:
            return

        try:
            recording_file = self.get_recording_filename()

            self.logger.info(f"Motion detected! Starting scare sequence")
            self.logger.info(f"Current video: {self.current_prefix}")
            self.logger.info(f"Recording to: {recording_file}")

            # Start recording (runs in background)
            record_cmd = self.get_record_command(recording_file)
            sub_record = sp.Popen(record_cmd)

            # Play scary video (wait for completion)
            self.logger.info(f"Playing scary video: {self.scare_file}")
            video_cmd = self.get_video_command(self.scare_file)
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

            # Check if we should rotate to a new video
            self.change_video()

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

    def validate_theme(self, theme: str) -> bool:
        """
        Validate that the specified theme exists in available themes.

        Args:
            theme: Theme name to validate

        Returns:
            True if valid, False otherwise
        """
        available = self.get_available_themes()
        if theme not in available:
            self.logger.error(
                f"Invalid theme '{theme}'. "
                f"Available themes: {', '.join(available)}"
            )
            return False
        return True

    def run(self, initial_theme: str, rotation_minutes: int):
        """
        Start the advanced scare system with video rotation.

        Args:
            initial_theme: Starting video theme
            rotation_minutes: Minutes between video rotations
        """
        # Validate theme
        if not self.validate_theme(initial_theme):
            sys.exit(1)

        # Set initial state
        self.current_prefix = initial_theme
        self.new_prefix = initial_theme
        self.rotation_minutes = rotation_minutes

        media_dir = self.config['paths']['media_dir']
        video_suffix = self.config['themes']['file_format']['video_suffix']
        self.scare_file = f"{media_dir}/{self.current_prefix}{video_suffix}"

        self.logger.info(f"Starting with theme: {initial_theme}")
        self.logger.info(f"Video rotation interval: {rotation_minutes} minutes")

        # Ensure recordings directory exists
        self.ensure_recordings_dir()

        # Show initial image
        self.show_image(initial_theme)

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
    if len(sys.argv) < 3:
        print("Usage: python3 scarerandom.py [VideoName] [Minutes]")
        print("Example: python3 scarerandom.py Male 10")
        print("\n[VideoName] must be one of the themes in config.yaml")
        print("[Minutes] is how often to rotate to a different video")
        sys.exit(1)

    try:
        video_name = sys.argv[1]

        # Validate minutes argument
        if not sys.argv[2].isdigit():
            print(f"ERROR: Minutes must be a number, got: {sys.argv[2]}")
            sys.exit(1)

        rotation_minutes = int(sys.argv[2])

        if rotation_minutes <= 0:
            print("ERROR: Minutes must be greater than 0")
            sys.exit(1)

        # Create and run system
        scare = AdvancedScareSystem()
        scare.run(video_name, rotation_minutes)

    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
