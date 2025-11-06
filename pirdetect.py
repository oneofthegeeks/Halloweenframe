#!/usr/bin/env python3
"""
PIR Motion Sensor Detector Module
Monitors a GPIO pin connected to a PIR motion sensor and triggers callbacks on state changes.
"""

import time
import os
import logging
from typing import Callable, List

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("WARNING: RPi.GPIO not available. Running in mock mode for development.")
    # Mock GPIO for development/testing on non-Raspberry Pi systems
    class MockGPIO:
        BOARD = 10
        BCM = 11
        IN = 1
        OUT = 0
        HIGH = 1
        LOW = 0
        PUD_DOWN = 21
        PUD_UP = 22

        @staticmethod
        def setmode(mode):
            pass

        @staticmethod
        def setup(pin, mode, pull_up_down=None):
            pass

        @staticmethod
        def input(pin):
            return False

        @staticmethod
        def cleanup():
            pass

    GPIO = MockGPIO()


class Detector:
    """
    PIR Motion Sensor Detector

    Monitors a GPIO pin and triggers registered callbacks when motion is detected.
    """

    def __init__(self, sensor_pin: int, pin_mode: str = "BOARD", pull_mode: str = "DOWN"):
        """
        Initialize the motion detector.

        Args:
            sensor_pin: GPIO pin number where PIR sensor is connected
            pin_mode: GPIO numbering mode ("BOARD" or "BCM")
            pull_mode: Pull resistor mode ("UP" or "DOWN")
        """
        self.callbacks: List[Callable] = []
        self.sensor = sensor_pin
        self.curr_state = False
        self.prev_state = False
        self.logger = logging.getLogger(__name__)

        try:
            # Set GPIO mode
            mode = GPIO.BOARD if pin_mode == "BOARD" else GPIO.BCM
            GPIO.setmode(mode)

            # Set pull-up/down mode
            pull = GPIO.PUD_DOWN if pull_mode == "DOWN" else GPIO.PUD_UP

            # Setup sensor pin
            GPIO.setup(self.sensor, GPIO.IN, pull_up_down=pull)
            self.logger.info(f"GPIO pin {self.sensor} initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize GPIO: {e}")
            raise

    def read(self) -> bool:
        """
        Read current sensor state.

        Returns:
            Current state of the sensor (True = motion detected)
        """
        try:
            self.prev_state = self.curr_state
            self.curr_state = bool(GPIO.input(self.sensor))
            return self.curr_state
        except Exception as e:
            self.logger.error(f"Error reading sensor state: {e}")
            return False

    def print_state(self):
        """Print the current state of the sensor to console."""
        state_str = "HIGH" if self.curr_state else "LOW"
        message = f"GPIO pin {self.sensor} is {state_str}"
        self.logger.info(message)
        print(message)

    def subscribe(self, callback: Callable[[bool], None]):
        """
        Register a callback function to be called on state changes.

        Args:
            callback: Function to call when motion state changes.
                     Should accept one boolean parameter (state).
        """
        if not callable(callback):
            raise ValueError("Callback must be callable")
        self.callbacks.append(callback)
        self.logger.debug(f"Callback registered: {callback.__name__}")

    def trigger_callbacks(self, state: bool):
        """
        Execute all registered callbacks with the current state.

        Args:
            state: Current motion detection state
        """
        for callback in self.callbacks:
            try:
                callback(state)
            except Exception as e:
                self.logger.error(f"Error in callback {callback.__name__}: {e}")

    def start(self, poll_interval: float = 0.1):
        """
        Start monitoring the sensor.

        Args:
            poll_interval: Time in seconds between sensor checks
        """
        try:
            self.logger.info("Starting motion detection")
            self.read()
            self.print_state()

            while True:
                self.read()
                if self.curr_state != self.prev_state:
                    self.print_state()
                    self.trigger_callbacks(self.curr_state)
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            self.logger.info("Motion detection stopped by user")
            self.cleanup()
        except SystemExit:
            self.logger.info("System exit requested")
            self.cleanup()
        except Exception as e:
            self.logger.error(f"Unexpected error in motion detection loop: {e}")
            self.cleanup()
            raise

    def cleanup(self):
        """Clean up GPIO and restore terminal state."""
        try:
            GPIO.cleanup()
            # Since fbi doesn't restore the console correctly, fix terminal
            os.system('stty sane')
            self.logger.info("Cleanup completed successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Backward compatibility alias
detector = Detector
