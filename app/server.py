from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host=app.config["server"]["host"],
        port=app.config["server"]["port"],
    )
