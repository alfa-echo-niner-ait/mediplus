from flask import Blueprint, render_template, redirect, url_for
from .forms import LoginForm

home = Blueprint('home', __name__)


@home.route('/', methods=['GET', 'POST'])
def index():
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        username = loginForm.username.data
        password = loginForm.password.data
        remember = loginForm.remember.data
        
        print(f"User: {username}\nPass: {password}\nRemember: {remember}")
        return redirect(url_for('home.index'))
        
    return render_template('home/index.html', loginForm=loginForm)
