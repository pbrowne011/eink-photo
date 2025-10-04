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
cp config/config.example.toml config/config.toml
# Edit config.toml with your settings
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
