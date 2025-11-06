#!/usr/bin/env python3
"""
Basic Scare Script
Displays a static image and plays a scary video when motion is detected.

Usage: python3 scare.py [VideoName]
Example: python3 scare.py Male
"""

import subprocess as sp
import time
import os
import sys
import logging
from pathlib import Path
from typing import Optional
import yaml

from pirdetect import Detector


class ScareSystem:
    """Basic scare system with motion detection and video playback."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the scare system.

        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.video_name: Optional[str] = None
        self.detector: Optional[Detector] = None

    def load_config(self, config_path: str) -> dict:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file

        Returns:
            Configuration dictionary
        """
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
                'media_dir': '/home/pi/Projects/Halloween/ScareMedia'
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

    def validate_media_files(self, video_name: str) -> bool:
        """
        Check if required media files exist.

        Args:
            video_name: Name of the video theme

        Returns:
            True if all files exist, False otherwise
        """
        media_dir = self.config['paths']['media_dir']
        video_suffix = self.config['themes']['file_format']['video_suffix']
        image_suffix = self.config['themes']['file_format']['image_suffix']

        video_path = Path(media_dir) / f"{video_name}{video_suffix}"
        image_path = Path(media_dir) / f"{video_name}{image_suffix}"

        if not video_path.exists():
            self.logger.error(f"Video file not found: {video_path}")
            return False

        if not image_path.exists():
            self.logger.error(f"Image file not found: {image_path}")
            return False

        return True

    def get_video_command(self, video_path: str) -> list:
        """
        Build video playback command from config.

        Args:
            video_path: Path to video file

        Returns:
            Command list for subprocess
        """
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

    def show_image(self, video_name: str):
        """
        Display static start image on framebuffer.

        Args:
            video_name: Name of the video theme
        """
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

        Args:
            curr_state: Current motion sensor state
        """
        if not curr_state:
            return

        try:
            media_dir = self.config['paths']['media_dir']
            video_suffix = self.config['themes']['file_format']['video_suffix']
            scare_file = f"{media_dir}/{self.video_name}{video_suffix}"

            self.logger.info(f"Motion detected! Playing video: {scare_file}")

            video_cmd = self.get_video_command(scare_file)
            sub_video = sp.Popen(video_cmd)

            # Wait for video to complete
            while sub_video.poll() is None:
                time.sleep(0.1)

            self.logger.info("Video playback completed")

        except Exception as e:
            self.logger.error(f"Error during video playback: {e}")

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
        Start the scare system.

        Args:
            video_name: Name of the video theme to use
        """
        self.video_name = video_name

        # Validate media files
        if not self.validate_media_files(video_name):
            self.logger.error("Required media files not found. Exiting.")
            sys.exit(1)

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
        print("Usage: python3 scare.py [VideoName]")
        print("Example: python3 scare.py Male")
        sys.exit(1)

    video_name = sys.argv[1]

    try:
        scare = ScareSystem()
        scare.run(video_name)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
