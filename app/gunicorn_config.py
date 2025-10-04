import tomli

# Load configuration
try:
    with open('config/config.toml', 'rb') as f:
        _config = tomli.load(f)
    bind = f"{_config['server']['host']}:{_config['server']['port']}"
except (FileNotFoundError, KeyError):
    bind = "0.0.0.0:8080"

workers = 2
timeout = 30