# eink-photo

A digital photo display running on a Raspberry Pi. Upload photos through a
simple web interface and display them on a Waveshare e-paper display.

## TODO
  * [ ] Create podman container for users to run if they desire
  * [ ] Add bun/typescript download to `runserver.sh` (see below)

  * [ ] Edit UI features
    * [ ] Lazy load photos on site (paginate? - probably not worth it)
    * [ ] Cache photos in browser
  * [ ] Update this README to be more relevant
    * [ ] Add photos of the site
    * [ ] Add photos of the eink display (with and without frame)
    * [ ] Add links to documentation to set up the Pi, purchase materials, etc.
  * [ ] Add steps to configure mDNS to allow for non-IP address website names
  * [ ] Add explanations to code - more documentation is better

### Things to add to `runserver.sh`
- check if bun is installed
- echo message "curl -fsSL https://bun.sh/install | bash" if one wants to do it
  that way
- add messages warning that this is insecure to script

- add line `bun build ./app/static/ts/upload.ts --outdir ./app/static/js/` to
- build artifact, add error check
- add --production flag to this README if not already here

### Podman
- apparently already included with Raspian?
  https://forums.raspberrypi.com/viewtopic.php?t=340525
- site https://podman.io/docs/installation

## Requirements

### Hardware
- Raspberry Pi ([Zero W](https://github.com/pbrowne011/eink-photo.git) or
  better). The board should have WiFi capabilites or the ability to connect to
  your router with an Ethernet cable.
- Waveshare e-paper display. Currently, this project only works with the
  [Waveshare 7.5in v2
  display](https://github.com/pbrowne011/eink-photo.git). The intent is that
  this will eventually work with other Waveshare displays, and possibly other
  eink displays in the future. For now, it is restricted to this one display.
  - Ensure that the device has an SPI interface shield. You will use this as a
    hat for the Pi Zero W. The ribbon from the display cannot be connected to
    the Pi directly. If using a different Rapsberry Pi, you'll need a different
    hat to connect the SPI ports.
- [SD card](https://github.com/pbrowne011/eink-photo.git) for the Pi OS. I'd
  recommend 16GB or higher so that you don't have to think about storage.
- Power supply for the Pi. The Zero W uses Micro-B, so you'll need a cable and
  an adaptor for it.

## Project Structure
```
photoframe/
├── config/          # Configuration files
├── app/             # Flask app
│   ├── lib/         # Waveshare code
│   ├── static/      # Frontend code
│   │   ├── css/
│   │   └── ts/
│   └── templates/   # HTML templates
├── tests/           # Bad "tests"
└── photos/          # Directory for uploaded photos
    ├── originals/
    └── display/
```

The Waveshare library code was taken from the [e-Paper
repository](https://github.com/waveshareteam/e-Paper). It is a Python library
combined with shared object files. View [`setup.py`](./app/lib/setup.py) for the
full list of dependencies, which includes
[`spidev`](https://pypi.org/project/RPi.GPIO/) and
[RPi.GPIO](https://pypi.org/project/RPi.GPIO/) (for Raspberry Pi
machines). These dependencies should allow this project to be used with a wide
variety of Pis and Waveshare displays. However, this has only been tested
against one Raspberry Pi and one Waveshare display.

## Configuration

Key configuration options in `config.toml`:

```toml
[display]
  width = 800
  height = 480
  orientation = "landscape"
  refresh_hours = 12

[server]
  port = 2323
  host = "0.0.0.0"

[waveshare]
  model = "EPD_7in5_V2"
  rotation = 0
```

The only settings that are used by the application currently are `server.port`
and `server.host`. The rest are intended features to be added in the future to
support more Waveshare displays

## Deployment

### Raspberry Pi Setup & Startup Configuration

#### Initial Setup
1. Flash [Raspberry Pi OS
   Lite](https://www.raspberrypi.com/software/operating-systems/) to SD
   card. There are a few guides that explain how to do this.
2. Enable SSH and configure WiFi on the Pi. This can be done when flashing the
   OS as part of the advanced configuration settings. Alternatively, you can
   modify using the `raspi-config` CLI when the board is hooked up to a display
   and I/O devices to do so.
3. On the Pi, clone this repository:
   ```bash
   git clone https://github.com/pbrowne011/eink-photo.git
   cd eink-photo
   ```

#### Install Dependencies
```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Install system dependencies for e-paper display
# FIXME(pjb) determine if python3-dev includes swig and liblgpio-dev by default
sudo apt update
sudo apt install -y python3-dev python3-pip git nginx
```

#### Configure for Startup

You are running a server on your Pi. You'll want this program to always start on
startup. This way, you won't have to deal with issues of trying to start it over
SSH or problems when the power cord is unplugged.

**Option 1: systemd service**
1. Create service file:
   ```bash
   sudo tee /etc/systemd/system/eink-photo.service > /dev/null << 'EOF'
   [Unit]
   Description=E-Ink Photo Frame
   After=network.target
   Wants=network-online.target
   
   [Service]
   Type=exec
   User=pi
   Group=pi
   WorkingDirectory=/home/pi/eink-photo
   ExecStart=/home/pi/eink-photo/runserver.sh --production
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   EOF
   ```

2. Enable and start service:
   ```bash
   sudo systemctl enable eink-photo.service
   sudo systemctl start eink-photo.service
   ```

**Option 2: crontab (Alternative)**
```bash
# Add to crontab for user pi
crontab -e

# Add this line:
@reboot cd /home/pi/eink-photo && ./runserver.sh --production >> /var/log/eink-photo.log 2>&1
```

#### Access Configuration
The application will be available at:
- `http://[pi-ip-address]` (production mode with nginx)
- `http://raspberrypi.local` (if
  [mDNS](https://shop.sandisk.com/product-portfolio/memory-cards/microsd-cards)
  is configured)
  
#### mDNS
TODO: add documentation on configuring mDNS for the Pi here

#### Troubleshooting Startup
```bash
# Check service status
sudo systemctl status eink-photo.service

# View logs
sudo journalctl -u eink-photo.service -f

# Restart service
sudo systemctl restart eink-photo.service
```

## Troubleshooting

TODO: add problems I encounter here

## License

This project is licensed under the GNU GPL 3.0.
