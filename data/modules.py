from flask import flash, redirect, url_for
from data.models import User, Plant, Comment
from data import db
import re


# This checks if the password contains letters, numbers and symbols
def check_password(password):
    has_alpha = re.search(r'[a-zA-Z]', password) is not None
    has_num = re.search(r'[0-9]', password) is not None
    has_symbol = re.search(r'[^a-zA-Z0-9]', password) is not None

    if has_alpha and has_num and has_symbol and len(password) >= 8:
        return 'valid'
    return None


def logged_in(session):
    if 'user' in session:
        flash('User has already logged in', 'info')
        return redirect(url_for('home'))


def not_logged_in(session):
    if 'user' not in session:
        flash('Log in please', 'info')
        return redirect(url_for('signin'))


def get_login_details(body):
    username = str(body['username']).strip()
    password = str(body['password']).strip()
    return username, password


def get_signup_details(body):
    # Gets users data to be stored in the database
    name = str(body['name']).strip()
    username = str(body['username']).strip()
    email = str(body['email']).lower().strip()
    password = str(body['password']).strip()
    return name, username, email, password


def get_review_info(body):
    rate = int(body['rate'])
    feedback = str(body['feedback']).strip()
    return rate, feedback


def exception_error(e, path):
    print(str(e))
    flash('Error occurred try again', 'danger')
    return redirect(url_for(path))


def add_user(name, username, email, password):
    new_user = User(username=username, name=name, email=email)
    new_user.password = password
    db.session.add(new_user)
    db.session.commit()


def add_comment(feedback, rate, username):
    new_review = Comment(comment=feedback, rate=rate, username=username)
    db.session.add(new_review)
    db.session.commit()


def get_profile_data(username):
    user = User.query.filter_by(username=username).first()
    plant_count = Plant.query.filter_by(username=username).count()
    return {
        'username': user.username,
        'name': user.name,
        'email': user.email,
        'upload': plant_count
    }


def delete_user(username):
    user = User.query.filter_by(username=username).first()
    # Assuming `get_plants` returns a list of plant objects
    plants = Plant.query.filter_by(username=username).all()
    if user and plants:
        # Delete all associated plants
        for plant in plants:
            db.session.delete(plant)
        # Delete the user
        db.session.delete(user)
        # Commit the transaction
        db.session.commit()
        return 'success'
    return None


def get_passwords(body):
    oldPassword = str(body['oldPassword']).strip()
    newPassword = str(body['newPassword']).strip()
    passwordConfirmation = str(body['newPasswordConfirmation']).strip()
    return oldPassword, newPassword, passwordConfirmation


def get_emails(body):
    oldPassword = str(body['oldPassword']).strip()
    oldEmail = str(body['oldEmail']).lower().strip()
    newEmail = str(body['newEmail']).lower().strip()
    return oldPassword, oldEmail, newEmail
