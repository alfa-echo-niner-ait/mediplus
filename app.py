from src import create_app
import src.users

app = create_app()


if __name__ == "__main__":
    app.run(debug=False)
    # set debug=True for local run