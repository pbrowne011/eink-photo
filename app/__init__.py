from flask import Flask
from pathlib import Path
import logging
import tomli

def load_config():
    config_path = Path("config/config.toml")
    with open(config_path, "rb") as f:
        return tomli.load(f)

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        config = load_config()
        app.config.update(config)
    else:
        app.config.update(test_config)
    
    photos_dir = Path("photos")
    (photos_dir / "originals").mkdir(parents=True, exist_ok=True)
    (photos_dir / "display").mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    from .routes import main
    app.register_blueprint(main)
    app.display_queue = DisplayQueue(app.config)
    
    return app
