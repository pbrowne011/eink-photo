#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[*]${NC} $1"; }
print_error() { echo -e "${RED}[!]${NC} $1"; }

VENV_CREATED=0

if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    VENV_CREATED=1
fi

source .venv/bin/activate

if [ $VENV_CREATED -eq 1 ]; then
    print_status "Installing dependencies..."
    if command -v uv >/dev/null 2>&1; then
        uv pip install -r requirements.txt
    else
        uv pip install --upgrade pip
        uv pip install -r requirements.txt
    fi
fi

if [ ! -f "config/config.toml" ]; then
    print_error "config/config.toml not found!"
    print_status "Creating default configuration..."

    mkdir -p config
    cat > config/config.toml <<EOF
[display]
  width = 800
  height = 480
  orientation = "landscape"
  refresh_hours = 12
  buffer_size = 10

[server]
  port = 8080
  host = "0.0.0.0"
  max_upload_size_mb = 10

[waveshare]
  model = "EPD_7in5_V2"
  rotation = 0
EOF
fi
    
eval "$(python3 - << EOF
import tomli
try:
    config = tomli.load(open('config/config.toml', 'rb'))
    print(f'export FLASK_HOST="{config["server"]["host"]}"')
    print(f'export FLASK_PORT={config["server"]["port"]}')
    print(f'export CONFIG_LOADED=1')
except KeyError as e:
    print('print_error "Missing required configuration key: {e}"')
    exit(1)
except Exception as e:
    print('print_error "Error loading config: {e}"')
    exit(1)
EOF
)"

if [ "$CONFIG_LOADED" -ne 1 ]; then
    print_error "Configuration loading failed. Exiting."
    exit 1
fi

export FLASK_APP="app.server:app"
export FLASK_ENV="development"
export PYTHONPATH="$PWD"

print_status "Starting Flask server at http://$FLASK_HOST:$FLASK_PORT"
flask run --host="$FLASK_HOST" --port="$FLASK_PORT"
