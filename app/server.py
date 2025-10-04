from app import create_app

app = create_app()

if __name__ == "__main__":
    config = app.config
    app.run(
        host=config["server"]["host"],
        port=config["server"]["port"],
    )
