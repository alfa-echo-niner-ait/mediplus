from src import create_app
import src.users

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
    # set debug=True for local run
    # set debug=False for deployment
