#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[*]${NC} $1"; }
print_error() { echo -e "${RED}[!]${NC} $1"; }

UV_CMD=$(which uv 2>/dev/null)
if [[ -z "$UV_CMD" ]]; then
    print_error "uv is required but not installed."
    print_error "Please install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if [[ ! -d ".venv" ]]; then
    print_status "Creating virtual environment..."
    "$UV_CMD" venv .venv
fi

# shellcheck source=/dev/null # added for peace of mind
source .venv/bin/activate

print_status "Checking and installing dependencies with uv..."
"$UV_CMD" pip install -r requirements.txt

if [[ ! -f "config/config.toml" ]]; then
    print_error "config/config.toml not found!"
    print_status "Creating default configuration..."

    mkdir -p config
    cat > config/config.toml <<EOF
[display]
  width = 800
  height = 480
  orientation = "landscape"
  refresh_hours = 12

[server]
  port = 8080
  host = "127.0.0.1"

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
    print(f'print_error "Missing required configuration key: {e}"')
    exit(1)
except Exception as e:
    print(f'print_error "Error loading config: {e}"')
    exit(1)
EOF
)"

if [[ "$CONFIG_LOADED" -ne 1 ]]; then
    print_error "Configuration loading failed. Exiting."
    exit 1
fi

export PYTHONPATH="$PWD"

# Setup nginx if in production mode and not already configured
setup_nginx() {
    if [[ ! -f "/etc/nginx/sites-enabled/eink-photo" ]]; then
        print_status "Setting up nginx reverse proxy..."
        
        if ! command -v nginx >/dev/null 2>&1; then
            print_status "Installing nginx..."
            sudo apt update && sudo apt install -y nginx
        fi
        
        print_status "Configuring nginx..."
        sudo cp ./config/nginx.conf /etc/nginx/sites-available/eink-photo
        sudo ln -sf /etc/nginx/sites-available/eink-photo /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        
        if sudo nginx -t; then
            print_status "Starting nginx..."
            sudo systemctl enable nginx
            sudo systemctl reload nginx
        else
            print_error "nginx configuration test failed!"
            exit 1
        fi
    fi
}

# Check if production mode is requested
if [[ "$1" == "--production" ]]; then
    export EINK_DISPLAY="true"
    setup_nginx
    print_status "Starting production server with gunicorn at http://$FLASK_HOST:$FLASK_PORT"
    print_status "Access your app at: http://$(hostname).local or http://$(hostname -I | cut -d' ' -f1)"
    gunicorn -c app/gunicorn_config.py app.server:app
else
    export FLASK_APP="app.server:app"
    export FLASK_ENV="development"
    export FLASK_DEBUG=1
    
    print_status "Starting Flask development server at http://$FLASK_HOST:$FLASK_PORT"
    flask run --host="$FLASK_HOST" --port="$FLASK_PORT"
fi
