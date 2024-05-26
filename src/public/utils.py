import os
import datetime
from datetime import date
import secrets
from PIL import Image, ImageOps
from flask import current_app


def get_datetime():
    """
    Return list [date, time]
    """
    date_now = date.today()
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    return [date_now, time_now]


def profile_picture_remover(picture_name, user_role):
    """
    ### Input:
    #### 1. picture_name
            - Pass the current avatar file name if exists
            - Remove the avatar file from the system
    #### 2. user_role
            - Pass the user role with small letters
            - Roles: patient, doctor, manager
    ### Return: None
    """
    os.remove(
        os.path.join(current_app.root_path, f"static/avatars/{user_role}", picture_name)
    )


def profile_picture_saver(picture_data, user_role) -> str:
    """
    ### Input:
    #### 1. picture_data
            - Pass the picture data received through form submission
            - Convert input picture to 600x600
            - Save it with random hex(12) name (24 char)
    #### 2. user_role
            - Pass the user role with small letters
            - Roles: patient, doctor, manager

    ### Return: Saved image file name
    """
    random_hex = secrets.token_hex(12)
    file_name, file_extension = os.path.splitext(picture_data.filename)
    picture_file_name = random_hex + file_extension
    picture_path = os.path.join(
        current_app.root_path, f"static/avatars/{user_role}", picture_file_name
    )

    output_size = (600, 600)
    image = Image.open(picture_data)
    image = ImageOps.exif_transpose(image)
    image.thumbnail(output_size, Image.Resampling.LANCZOS)
    image.save(picture_path)

    return picture_file_name
