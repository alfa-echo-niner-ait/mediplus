import os
from src import mail_manager
from src.users.models import Users
from flask_mail import Message
from flask import url_for, current_app


def reset_mail_sender(user):
    url = url_for(
        "public.reset_password",
        username=user.username,
        token=user.token,
        _external=True,
    )
    email = Message(
        subject="MediPlus Password Reset Link",
        sender="no_replay@mediplus.app",
        recipients=[user.email],
    )
    email.body = f"""<br>
               Dear <i>{user.username}</i>,
               <p>
               A password reset request has been submitted for your <b>MediPlus</b> account.
               Please follow the link below to reset your password.
               </p>
               <p>
               <b>Note: The link will expire in 10 minutes</b>
               </p>
               <p>
               <a href='{url}'>{url}</a>
                </p>
                <hr>
                <p>Thank you.</p>
                <br>"""
    print(email.body)
    email.html = email.body
    with current_app.app_context():
        mail_manager.connect()
        mail_manager.send(email)
