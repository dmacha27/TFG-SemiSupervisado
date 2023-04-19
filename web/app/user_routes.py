from flask import flash, render_template, redirect, url_for, Blueprint, request
from flask_login import login_user, login_required, logout_user
from flask_babel import gettext
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User
from . import db
from .forms import RegistrationForm, LoginForm

users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash(gettext('Loging successful!'), category='success')
                login_user(user)
                return redirect(url_for('main_bp.inicio'))
            else:
                form.password.errors.append(gettext('Incorrect password'))
        else:
            form.email.errors.append(gettext('Email not found'))

    return render_template('usuarios/login.html', form=form)


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_bp.inicio'))


@users_bp.route('/signup', methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        user = User.query.filter_by(email=email).first()
        if user:
            form.email.errors.append(gettext('Email already exists'))
            return render_template("usuarios/registro.html", form=form)

        usuario = User()
        usuario.email = email
        usuario.name = name
        usuario.password = generate_password_hash(password, method='sha256')
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario, remember=True)
        flash(gettext('Account created!'), category='success')
        return redirect(url_for('main_bp.inicio'))

    return render_template("usuarios/registro.html", form=form)
