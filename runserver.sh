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
        pip install --upgrade pip
        pip install -r requirements.txt
    fi
fi

eval $(python3 - << EOF
import tomli
config = tomli.load(open('config/config.toml', 'rb'))
print(f'export FLASK_HOST="{config["server"]["host"]}"')
print(f'export FLASK_PORT={config["server"]["port"]}')
EOF
)

export FLASK_APP="app.server:app"
export FLASK_ENV="development"
export PYTHONPATH="$PWD"

print_status "Starting Flask server at http://$FLASK_HOST:$FLASK_PORT"
flask run --host=$FLASK_HOST --port=$FLASK_PORT
