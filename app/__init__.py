from flask import Flask
from pathlib import Path
import logging
import tomli

def load_config():
    try:
        config_path = Path("config/config.toml")
        with open(config_path, "rb") as f:
            return tomli.load(f)
    except Exception as e:
        print(f"Unexpected error loading config: {e}")
        exit(1)

def create_app():
    app = Flask(__name__)

    config = load_config()
    app.config.update(config)
    
    photos_dir = Path("photos")
    (photos_dir / "originals").mkdir(parents=True, exist_ok=True)
    (photos_dir / "display").mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    # Initialize display controller
    from .display import DisplayController
    app.display_controller = DisplayController(config)
    
    from .routes import main
    app.register_blueprint(main)
    
    return app
