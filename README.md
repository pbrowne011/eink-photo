# eink-photo

A lightweight, privacy-focused digital photo frame solution running on Raspberry
Pi. Upload photos through a simple web interface and display them on an e-paper
display.

## Features

- Local-only web interface for photo management
- Automatic photo conversion for e-paper display
- Directory organization for photos
- Status monitoring and display management
- No cloud services or external dependencies required
- Cross-browser support (Chrome, Firefox, Safari)

## Requirements

### Hardware
- Raspberry Pi (Zero W or better)
- E-paper display (Waveshare or compatible)
- SD card (16GB+ recommended)
- Power supply

### Software
- Python 3.9+
- TypeScript
- Flask
- SQLite3

## Project Structure
```
photoframe/
├── config/          # Configuration files
├── app/             # Python backend
│   ├── static/      # Frontend assets
│   │   ├── css/
│   │   └── ts/      # TypeScript sources
│   └── templates/   # HTML templates
├── tests/           # Test suite
└── photos/          # Photo storage
    ├── originals/
    └── display/
```

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
npm install          # For TypeScript dependencies
```

3. Configure:
```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your settings
```

4. Run development server:
```bash
flask run --host=0.0.0.0 --port=2323
```

5. Access web interface:
```
http://[device-ip]:2323
# or if mDNS configured:
http://photoframe.local:2323
```

## Configuration

Key configuration options in `config.toml`:

```toml
[display]
  width = 800
  height = 480
  orientation = "landscape"
  refresh_hours = 12
  buffer_size = 10            # photos before repeating

[server]
  port = 2323
  host = "0.0.0.0"
  max_upload_size_mb = 10

[waveshare]
  model = "EPD_7in5_V2"
  rotation = 0
```

## Development

1. Setting up development environment:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt npm install --dev

# Run TypeScript compiler in watch mode
npm run watch

# Run tests
pytest
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_converter.py

# Run with coverage
pytest --cov=app tests/
```

## Deployment

TODO: add setup instructions

## Troubleshooting

Common issues and solutions:

1. Photo upload fails
   - Check disk space
   - Verify file permissions
   - Check upload size limits

2. Display not updating
   - Check display connection
   - Verify display configuration
   - Check logs in /var/log/photoframe/

3. Cannot access web interface
   - Verify network connection
   - Check firewall settings
   - Confirm service is running

## License

GNU GPL 3.0
