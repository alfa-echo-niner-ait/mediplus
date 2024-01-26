from src import create_app, login_manager
from src.users.models import Users

app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True)

