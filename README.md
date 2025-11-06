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
- Python 2.7+ (scripts use Python 2 syntax)
- **RPi.GPIO** - GPIO library for Python
- **omxplayer** - Raspberry Pi video player
- **raspivid** - Raspberry Pi camera utility
- **fbi** - Framebuffer image viewer

## Project Files

### Core Files

| File | Description | Features |
|------|-------------|----------|
| **pirdetect.py** | Motion detector class | GPIO-based PIR sensor monitoring with callback support |
| **scare.py** | Basic scare script | Image display + video playback on motion |
| **scare2.py** | Enhanced scare script | Adds reaction recording and playback |
| **scarerandom.py** | Advanced scare script | Multiple videos, timed rotation, reaction recording |

### Script Comparison

#### scare.py (Basic)
- Single video configuration
- Simple motion trigger → play video workflow
- Good for testing or simple setups

**Usage:**
```bash
python scare.py [VideoName]
```
Example: `python scare.py Male`

#### scare2.py (Enhanced)
- Single video + reaction recording
- Records 5-second video of person's reaction
- Plays back reaction after scary video
- Display rotated 180° (for upside-down mounting)

**Usage:**
```bash
python scare2.py [VideoName]
```

#### scarerandom.py (Advanced)
- Rotates through multiple videos (Male, Female, Child)
- Changes to new random video every N minutes
- Records reactions with timestamps
- Never plays same video twice in a row
- Most configurable option

**Usage:**
```bash
python scarerandom.py [VideoName] [Minutes]
```
Example: `python scarerandom.py Male 5` (starts with Male, rotates every 5 minutes)

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

### Display Settings
All scripts use these display settings:
- **Resolution:** 1280x720
- **Orientation:** 180° rotation (scripts use `--orientation 180`)
- **Audio:** Volume set to -600 (very quiet/muted)
- **Output:** Both HDMI and composite

### GPIO Pin Configuration
- **PIR Sensor:** GPIO Pin 7 (BCM numbering)
- **Pin Mode:** Input with pull-down resistor

### Video Names (scarerandom.py)
To add more video themes, edit the `VideoNames` list in scarerandom.py:
```python
VideoNames = ["Male", "Female", "Child", "YourNewTheme"]
```

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
6. **Sound:** Adjust volume in scripts (change -600 to desired level)

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

## Future Improvements

Potential enhancements for later:
- [ ] Port to Python 3
- [ ] Add web interface for remote control
- [ ] Support for multiple motion sensors
- [ ] Configurable GPIO pins
- [ ] Settings file (JSON/YAML) instead of hardcoded paths
- [ ] Support for sound effects separate from videos
- [ ] Analytics (count of scares, peak times)
- [ ] Remote upload of recordings
- [ ] Live preview mode

## Notes

- Scripts use Python 2 syntax (may need updates for Python 3)
- Originally designed for Raspberry Pi 3 or earlier
- Volume is very quiet (-600) by default
- Display rotation assumes upside-down mounting
- Recordings saved as H.264 raw format (.h264)

## License

No license specified in repository.

## Credits

Created by: oneofthegeeks
Repository: https://github.com/oneofthegeeks/Halloweenframe
