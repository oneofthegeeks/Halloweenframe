# Halloweenframe Setup Guide

Complete installation and configuration guide for the Halloweenframe motion-activated scare system.

## Table of Contents
1. [Hardware Setup](#hardware-setup)
2. [Software Installation](#software-installation)
3. [Project Installation](#project-installation)
4. [Media Preparation](#media-preparation)
5. [Testing](#testing)
6. [Running on Boot](#running-on-boot)
7. [Troubleshooting](#troubleshooting)

---

## Hardware Setup

### Components Needed

1. **Raspberry Pi** (tested on Pi 3, should work on Pi 2/4/Zero W)
2. **PIR Motion Sensor** (HC-SR501 or similar)
3. **Raspberry Pi Camera Module** (v1 or v2)
4. **Display** (HDMI monitor or composite display)
5. **MicroSD Card** (16GB minimum, 32GB recommended)
6. **Power Supply** (official Raspberry Pi power supply recommended)
7. **Jumper Wires** (Female-to-Female, 3 wires needed)
8. **Speakers** (optional, for audio)

### PIR Sensor Wiring

Connect the PIR sensor to the Raspberry Pi GPIO pins:

```
PIR Sensor          Raspberry Pi
──────────────────────────────────
VCC (5V)    ───────> Pin 2 (5V)
GND         ───────> Pin 6 (Ground)
OUT         ───────> Pin 7 (GPIO 4)
```

**GPIO Pin Reference:**
```
     3V3  (1) (2)  5V       <- Connect PIR VCC here
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND      <- Connect PIR GND here
   GPIO4  (7) (8)  GPIO14   <- Connect PIR OUT here
     GND  (9) (10) GPIO15
```

### Camera Module Setup

1. Locate the camera connector (between HDMI and audio jack)
2. Gently pull up the plastic clip
3. Insert camera ribbon cable (blue side facing audio jack)
4. Push down the plastic clip to secure

### Display Connection

**HDMI Setup (Recommended):**
- Connect HDMI cable from Pi to monitor
- Most monitors auto-configure

**Composite Setup:**
- Connect RCA cable to yellow composite port
- May need to configure in /boot/config.txt

---

## Software Installation

### 1. Raspberry Pi OS Setup

**Fresh Installation:**
```bash
# Download Raspberry Pi Imager from:
# https://www.raspberrypi.org/software/

# Flash Raspberry Pi OS Lite or Desktop to SD card
# Boot the Pi and complete initial setup
```

**First Boot Configuration:**
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Enable camera and configure settings
sudo raspi-config
```

In raspi-config:
- Navigate to "Interface Options"
- Enable "Camera"
- Enable "SSH" (optional, for remote access)
- Reboot when prompted

### 2. Install Required Software

```bash
# Install Python GPIO library
sudo apt-get install python-rpi.gpio python3-rpi.gpio -y

# Install omxplayer (video player)
sudo apt-get install omxplayer -y

# Install fbi (framebuffer image viewer)
sudo apt-get install fbi -y

# Install git (to clone repository)
sudo apt-get install git -y

# raspivid should already be installed with Raspberry Pi OS
# Verify with:
raspivid --help
```

### 3. Test Camera

```bash
# Test camera with 5-second recording
raspivid -o test.h264 -t 5000

# If successful, you'll see test.h264 file
# Play it back with:
omxplayer test.h264
```

---

## Project Installation

### 1. Clone Repository

```bash
# Navigate to home directory
cd /home/pi

# Create Projects directory
mkdir -p Projects/Halloween
cd Projects/Halloween

# Clone the repository
git clone https://github.com/oneofthegeeks/Halloweenframe.git
cd Halloweenframe
```

### 2. Create Directory Structure

```bash
# Create media directories
mkdir -p /home/pi/Projects/Halloween/ScareMedia
mkdir -p /home/pi/Projects/Halloween/Recordings

# Verify structure
ls -la /home/pi/Projects/Halloween/
```

### 3. Set Permissions

```bash
# Make Python scripts executable
chmod +x *.py

# Ensure write access to Recordings folder
chmod 777 /home/pi/Projects/Halloween/Recordings
```

---

## Media Preparation

### 1. Video Requirements

**Format Specifications:**
- Container: MP4
- Video Codec: H.264
- Audio Codec: AAC
- Resolution: 1280x720 (or lower)
- Framerate: 24-30 fps

**Converting Videos:**
```bash
# If you need to convert videos, install ffmpeg:
sudo apt-get install ffmpeg -y

# Convert video to compatible format:
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -s 1280x720 -r 30 output.mp4
```

### 2. Image Requirements

**Format Specifications:**
- Format: PNG or JPG
- Resolution: 1280x720 (match your display)

**Creating Start Images:**
```bash
# Example: Convert/resize image with ImageMagick
sudo apt-get install imagemagick -y
convert input.jpg -resize 1280x720 -background black -gravity center -extent 1280x720 output.png
```

### 3. File Naming Convention

For each theme (e.g., "Male"), you need two files:

```
ScareMedia/
├── MaleScareV.mp4    # The scary video
├── MaleStart.png     # The static image shown while waiting
├── FemaleScareV.mp4
├── FemaleStart.png
├── ChildScareV.mp4
└── ChildStart.png
```

**Naming Pattern:**
- Video: `[ThemeName]ScareV.mp4`
- Image: `[ThemeName]Start.png`

### 4. Transfer Media Files

**Option 1: USB Drive**
```bash
# Mount USB drive
sudo mount /dev/sda1 /mnt

# Copy files
cp /mnt/*.mp4 /home/pi/Projects/Halloween/ScareMedia/
cp /mnt/*.png /home/pi/Projects/Halloween/ScareMedia/

# Unmount
sudo umount /mnt
```

**Option 2: SCP (from another computer)**
```bash
# From your computer:
scp *.mp4 pi@raspberrypi.local:/home/pi/Projects/Halloween/ScareMedia/
scp *.png pi@raspberrypi.local:/home/pi/Projects/Halloween/ScareMedia/
```

**Option 3: SFTP Client**
Use FileZilla, Cyberduck, or similar SFTP client to transfer files

---

## Testing

### 1. Test PIR Sensor

```bash
cd /home/pi/Projects/Halloween/Halloweenframe

# Run a simple test
python -c "
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print('Wave hand in front of sensor...')
for i in range(30):
    if GPIO.input(7):
        print('MOTION DETECTED!')
    else:
        print('No motion')
    time.sleep(1)

GPIO.cleanup()
"
```

### 2. Test Basic Scare Script

```bash
# Test with scare.py (simplest version)
python scare.py Male

# Expected behavior:
# 1. Static image appears on display
# 2. Wave hand in front of PIR sensor
# 3. Scary video should play
# 4. Returns to static image
#
# Press Ctrl+C to exit
```

### 3. Test with Recording

```bash
# Test scare2.py (with recording)
python scare2.py Female

# Expected behavior:
# 1. Static image appears
# 2. Wave hand in front of sensor
# 3. Camera records for 5 seconds while video plays
# 4. Your recording plays back
# 5. Returns to static image
#
# Check recordings:
ls -lh /home/pi/Projects/Halloween/Recordings/
```

### 4. Test Random Rotation

```bash
# Test scarerandom.py (rotate every 1 minute for testing)
python scarerandom.py Male 1

# Expected behavior:
# 1. Starts with Male theme
# 2. After 1 minute, switches to random theme
# 3. Records reactions for each trigger
#
# Watch console output for rotation messages
```

---

## Running on Boot

### Option 1: Systemd Service (Recommended)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/halloweenframe.service
```

Add this content:
```ini
[Unit]
Description=Halloween Frame Scare System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Projects/Halloween/Halloweenframe
ExecStart=/usr/bin/python /home/pi/Projects/Halloween/Halloweenframe/scarerandom.py Male 10
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable halloweenframe.service

# Start service now
sudo systemctl start halloweenframe.service

# Check status
sudo systemctl status halloweenframe.service

# View logs
sudo journalctl -u halloweenframe.service -f
```

### Option 2: rc.local (Simple Method)

```bash
sudo nano /etc/rc.local
```

Add before `exit 0`:
```bash
# Start Halloween Frame
cd /home/pi/Projects/Halloween/Halloweenframe
python scarerandom.py Male 10 &
```

### Option 3: Crontab

```bash
crontab -e
```

Add this line:
```
@reboot sleep 30 && cd /home/pi/Projects/Halloween/Halloweenframe && python scarerandom.py Male 10
```

---

## Troubleshooting

### PIR Sensor Issues

**Problem:** No motion detected

**Solutions:**
1. Check wiring connections
2. Adjust sensitivity potentiometer on sensor (small orange knob)
3. Adjust delay potentiometer (second knob)
4. Verify power to sensor (LED should light up)
5. Test with multimeter (OUT pin should go HIGH when motion detected)

### Camera Issues

**Problem:** Camera not working

**Solutions:**
```bash
# Check if camera is enabled
vcgencmd get_camera

# Should show: supported=1 detected=1

# If not, enable in raspi-config:
sudo raspi-config
# Interface Options -> Camera -> Enable

# Check camera cable connection (blue side toward audio jack)

# Test camera directly:
raspistill -o test.jpg
```

### Video Playback Issues

**Problem:** Video won't play or black screen

**Solutions:**
```bash
# Test omxplayer directly:
omxplayer /home/pi/Projects/Halloween/ScareMedia/MaleScareV.mp4

# Check video file:
file /home/pi/Projects/Halloween/ScareMedia/MaleScareV.mp4

# Re-encode if needed:
ffmpeg -i original.mp4 -c:v libx264 -preset fast -crf 22 -c:a aac MaleScareV.mp4
```

### Display Issues

**Problem:** Display rotated wrong direction

**Solution:**
Edit the script and change `--orientation 180` to:
- `0` for normal
- `90` for 90° rotation
- `180` for 180° rotation (current)
- `270` for 270° rotation

### Permission Issues

**Problem:** Can't write recordings

**Solutions:**
```bash
# Fix permissions on Recordings folder:
sudo chmod 777 /home/pi/Projects/Halloween/Recordings

# Fix ownership:
sudo chown -R pi:pi /home/pi/Projects/Halloween
```

### Script Won't Start

**Problem:** ImportError or script errors

**Solutions:**
```bash
# Verify Python and libraries:
python --version
python -c "import RPi.GPIO; print('GPIO OK')"

# Run script with error output:
python scarerandom.py Male 10 2>&1 | tee error.log

# Check the error log:
cat error.log
```

---

## Advanced Configuration

### Adjusting Audio Volume

Edit the script and change `-o both --vol -600` to:
- `-o both --vol 0` for full volume
- `-o both --vol -300` for medium volume
- `-o both --vol -1000` for quieter
- `-o hdmi --vol -600` for HDMI audio only
- `-o local --vol -600` for 3.5mm jack only

### Adding More Themes

1. Add video and image files to ScareMedia:
   - `NewThemeScareV.mp4`
   - `NewThemeStart.png`

2. Edit scarerandom.py, find this line:
```python
VideoNames = ["Male", "Female", "Child"]
```

3. Add your theme:
```python
VideoNames = ["Male", "Female", "Child", "NewTheme"]
```

### Changing GPIO Pin

Edit pirdetect.py, find:
```python
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
```

Change `7` to your desired pin number (BOARD numbering)

---

## Quick Reference

### Useful Commands

```bash
# Start script manually
python scarerandom.py Male 10

# Stop running script
# Press Ctrl+C or:
sudo killall python

# Check if script is running
ps aux | grep python

# View recent recordings
ls -lt /home/pi/Projects/Halloween/Recordings/ | head

# Delete old recordings
rm /home/pi/Projects/Halloween/Recordings/*

# Check disk space
df -h

# Monitor system temperature
vcgencmd measure_temp
```

### File Locations Quick Reference

```
/home/pi/Projects/Halloween/
├── Halloweenframe/          # Git repository
│   ├── pirdetect.py
│   ├── scare.py
│   ├── scare2.py
│   └── scarerandom.py
├── ScareMedia/              # Your videos and images
│   ├── [Theme]ScareV.mp4
│   └── [Theme]Start.png
└── Recordings/              # Reaction recordings
    └── [timestamp].h264
```

---

## Next Steps

After successful setup:
1. Test in daylight to verify operation
2. Adjust sensor sensitivity for your environment
3. Set up for dusk to ensure lighting is adequate for camera
4. Position display and camera at appropriate height
5. Run a full evening test before Halloween
6. Have backup SD card ready
7. Consider external battery pack for power outages

---

## Additional Resources

- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [PIR Sensor Guide](https://www.raspberrypi.org/documentation/usage/gpio/)
- [omxplayer Documentation](https://github.com/popcornmix/omxplayer)
- [Raspberry Pi Camera Documentation](https://www.raspberrypi.org/documentation/hardware/camera/)

## Support

For issues with this project, check:
- Original repository: https://github.com/oneofthegeeks/Halloweenframe
- Raspberry Pi Forums: https://forums.raspberrypi.com/
- Stack Overflow: Tag questions with `raspberry-pi` and `python`
