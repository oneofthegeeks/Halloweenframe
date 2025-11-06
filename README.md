# Halloweenframe

[![GitHub](https://img.shields.io/badge/GitHub-oneofthegeeks%2FHalloweenframe-blue?logo=github)](https://github.com/oneofthegeeks/Halloweenframe)

A Raspberry Pi-based motion-activated Halloween scare system that detects trick-or-treaters and triggers scary videos while recording their reactions.

## Overview

This project transforms a Raspberry Pi into an automated Halloween decoration that:
1. Displays a static image while waiting
2. Detects motion using a PIR sensor
3. Plays a scary video when triggered
4. Records the person's reaction (optional)
5. Plays back their reaction (optional)

## Hardware Requirements

- **Raspberry Pi** (any model with GPIO pins)
- **PIR Motion Sensor** (connected to GPIO pin 7)
- **Display** (HDMI or composite, supports 1280x720)
- **Raspberry Pi Camera Module** (required for scare2.py and scarerandom.py)
- **Power supply** for Raspberry Pi
- **Speakers/Audio output** (optional, for video sound)

## Software Requirements

- Raspberry Pi OS (formerly Raspbian)
- **Python 3.7+** (all scripts now use Python 3)
- **PyYAML** - YAML configuration file support
- **RPi.GPIO** - GPIO library for Python
- **omxplayer** - Raspberry Pi video player
- **raspivid** - Raspberry Pi camera utility
- **fbi** - Framebuffer image viewer

Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

## Project Files

### Core Files

| File | Description | Features |
|------|-------------|----------|
| **pirdetect.py** | Motion detector class | GPIO-based PIR sensor monitoring with callback support, error handling, mock mode for development |
| **scare.py** | Basic scare script | Image display + video playback on motion |
| **scare2.py** | Enhanced scare script | Adds reaction recording and playback |
| **scarerandom.py** | Advanced scare script | Multiple videos, timed rotation, reaction recording |
| **config.yaml** | Configuration file | All settings: GPIO pins, paths, video settings, camera settings, logging |
| **requirements.txt** | Python dependencies | List of required Python packages |

## ✨ What's New (Python 3 Update)

All scripts have been modernized with:
- **Python 3 compatibility** - Updated from Python 2 to Python 3.7+
- **Configuration file** - `config.yaml` for easy customization
- **Error handling** - Comprehensive try-catch blocks and logging
- **Type hints** - Modern Python type annotations
- **Logging system** - Detailed logs for debugging
- **Mock GPIO mode** - Development/testing on non-Pi systems
- **Path validation** - Checks for media files before running
- **Better documentation** - Docstrings for all functions

### Script Comparison

#### scare.py (Basic)
- Single video configuration
- Simple motion trigger → play video workflow
- Good for testing or simple setups

**Usage:**
```bash
python3 scare.py [VideoName]
```
Example: `python3 scare.py Male`

#### scare2.py (Enhanced)
- Single video + reaction recording
- Records 5-second video of person's reaction
- Plays back reaction after scary video
- Display rotated 180° (for upside-down mounting)

**Usage:**
```bash
python3 scare2.py [VideoName]
```

#### scarerandom.py (Advanced)
- Rotates through multiple videos (Male, Female, Child)
- Changes to new random video every N minutes
- Records reactions with timestamps
- Never plays same video twice in a row
- Most configurable option

**Usage:**
```bash
python3 scarerandom.py [VideoName] [Minutes]
```
Example: `python3 scarerandom.py Male 5` (starts with Male, rotates every 5 minutes)

## Directory Structure

The scripts expect the following directory structure on your Raspberry Pi:

```
/home/pi/Projects/Halloween/
├── ScareMedia/
│   ├── MaleScareV.mp4       # Scary video for Male theme
│   ├── MaleStart.png         # Static image shown while waiting
│   ├── FemaleScareV.mp4     # Scary video for Female theme
│   ├── FemaleStart.png       # Static image shown while waiting
│   ├── ChildScareV.mp4      # Scary video for Child theme
│   └── ChildStart.png        # Static image shown while waiting
└── Recordings/
    └── [timestamps].h264     # Reaction recordings (auto-generated)
```

## Configuration

All settings are now managed through `config.yaml`. Edit this file to customize your setup:

### Key Configuration Sections

**GPIO Settings:**
```yaml
gpio:
  pin_mode: BOARD      # GPIO numbering mode
  sensor_pin: 7        # PIR sensor pin
  pull_mode: DOWN      # Pull resistor mode
```

**File Paths:**
```yaml
paths:
  media_dir: /home/pi/Projects/Halloween/ScareMedia
  recordings_dir: /home/pi/Projects/Halloween/Recordings
```

**Video Playback:**
```yaml
video:
  resolution:
    width: 1280
    height: 720
  orientation: 180     # Display rotation
  volume: -600         # Audio volume
  aspect_mode: fill
```

**Camera Recording:**
```yaml
camera:
  duration: 5000       # Recording length in ms
  rotation: 180        # Camera rotation
```

**Video Themes:**
```yaml
themes:
  available:
    - Male
    - Female
    - Child
    # Add more themes here!
```

**Logging:**
```yaml
logging:
  enabled: true
  level: INFO          # DEBUG, INFO, WARNING, ERROR
  log_file: /home/pi/Projects/Halloween/halloweenframe.log
```

### Adding New Video Themes

1. Create video and image files:
   - `NewThemeScareV.mp4` (scary video)
   - `NewThemeStart.png` (waiting image)

2. Add theme name to `config.yaml`:
```yaml
themes:
  available:
    - Male
    - Female
    - Child
    - NewTheme  # Add here
```

3. No code changes needed!

## Installation & Setup

See [SETUP.md](SETUP.md) for detailed installation and configuration instructions.

## How It Works

### Motion Detection Flow
1. **pirdetect.py** continuously monitors GPIO pin 7
2. When motion is detected (pin goes HIGH), it triggers a callback
3. The callback function in the main script executes the scare sequence

### Scare Sequence (scarerandom.py)
1. Display static "Start" image using fbi
2. Wait for motion detection
3. When triggered:
   - Start camera recording (5 seconds)
   - Play scary video with omxplayer
   - Wait for video to finish
   - Play back the reaction recording
4. Return to step 1

### Video Rotation (scarerandom.py only)
- Timer runs in background
- Every N minutes, selects a new random video from the list
- Ensures different video than current one
- Updates both video and start image

## Usage Tips

1. **Testing:** Start with scare.py to verify hardware works
2. **Camera Check:** Use scare2.py to test camera recording
3. **Production:** Use scarerandom.py for actual Halloween night
4. **Positioning:** Mount display and camera facing trick-or-treaters
5. **Lighting:** Ensure enough light for camera, but dim for effect
6. **Sound:** Adjust volume in config.yaml (change -600 to desired level)
7. **Logging:** Enable DEBUG level in config.yaml for troubleshooting
8. **Development:** Test on non-Pi systems using built-in GPIO mock mode

## Troubleshooting

### No Motion Detection
- Check PIR sensor wiring (should be on GPIO pin 7)
- Verify sensor has power (usually 5V)
- Check sensor sensitivity adjustment knob

### Video Won't Play
- Ensure omxplayer is installed: `sudo apt-get install omxplayer`
- Verify video file paths match expected structure
- Check video file format (H.264 MP4 works best)

### Camera Not Recording
- Enable camera in raspi-config: `sudo raspi-config`
- Verify camera cable connection
- Check if raspivid works: `raspivid -o test.h264 -t 5000`

### Display Issues
- Check HDMI/composite connection
- Verify display resolution (1280x720)
- Try different orientation value if upside down

### Python/Configuration Issues
- **Import Error:** Run `pip3 install -r requirements.txt`
- **Config not found:** Ensure config.yaml is in the same directory as scripts
- **YAML parse error:** Check config.yaml syntax (proper indentation)
- **Permission denied:** Recordings directory needs write permissions
- **Check logs:** Review log file specified in config.yaml for detailed errors

## Future Improvements

Completed enhancements:
- [x] **Port to Python 3** - ✅ Complete! All scripts now Python 3.7+
- [x] **Configurable GPIO pins** - ✅ Now in config.yaml
- [x] **Settings file (YAML)** - ✅ All settings in config.yaml
- [x] **Error handling** - ✅ Comprehensive logging and error handling
- [x] **Type hints** - ✅ Modern Python type annotations

Potential future enhancements:
- [ ] Add web interface for remote control
- [ ] Support for multiple motion sensors
- [ ] Support for sound effects separate from videos
- [ ] Analytics (count of scares, peak times)
- [ ] Remote upload of recordings
- [ ] Live preview mode
- [ ] Video playback queue
- [ ] Mobile app control

## Notes

- **Python 3.7+** required (fully modernized from Python 2)
- Compatible with all Raspberry Pi models (Pi 2, 3, 4, Zero W)
- Volume is quiet (-600) by default - adjust in config.yaml
- Display rotation configurable in config.yaml
- Recordings saved as H.264 raw format (.h264)
- Mock GPIO mode allows development on non-Pi systems
- All settings centralized in config.yaml

## License

No license specified in repository.

## Credits

Created by: oneofthegeeks
Repository: https://github.com/oneofthegeeks/Halloweenframe
