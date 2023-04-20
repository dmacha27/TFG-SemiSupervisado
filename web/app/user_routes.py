import json

from flask import flash, render_template, redirect, url_for, Blueprint, request, session
from flask_login import login_user, login_required, logout_user
from flask_babel import gettext
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
from .models import User, Dataset
from . import db
from .forms import RegistrationForm, LoginForm, UserForm

users_bp = Blueprint('users_bp', __name__)


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_bp.inicio'))


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        email = request.form.get('email')
        password = request.form.get('password')

        usuario = User.query.filter_by(email=email).first()
        if usuario:
            if check_password_hash(usuario.password, password):
                flash(gettext('Loging successful!'), category='success')
                usuario.last_login = datetime.now()
                login_user(usuario)
                session.pop('ALGORITMO', None)
                session.pop('FICHERO', None)
                return redirect(url_for('main_bp.inicio'))
            else:
                form.password.errors.append(gettext('Incorrect password'))
        else:
            form.email.errors.append(gettext('Email not found'))

    return render_template('usuarios/login.html', form=form)


@users_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
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
        usuario.last_login = datetime.now()
        db.session.add(usuario)
        db.session.commit()
        login_user(usuario)
        session.pop('ALGORITMO', None)
        session.pop('FICHERO', None)
        flash(gettext('Account created!'), category='success')
        return redirect(url_for('main_bp.inicio'))

    return render_template("usuarios/registro.html", form=form)


@users_bp.route('/perfil/<user_id>', methods=['GET', 'POST'])
@login_required
def editar(user_id):
    form = UserForm(request.form)

    usuario = User.query.get(int(user_id))
    if not usuario:
        flash(gettext("User doesn't exist"))
        return redirect(url_for('main_bp.inicio'))

    errores = False
    if request.method == 'POST' and form.validate():
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        actual_password = request.form.get('actual_password')
        new_password = request.form.get('new_password')

        if not check_password_hash(usuario.password, actual_password):
            form.actual_password.errors.append(gettext('Incorrect actual password'))
            errores = True

        check_email = User.query.filter_by(email=new_email).first()
        if check_email and new_email != usuario.email:
            form.email.errors.append(gettext('Email already exists'))
            errores = True

        if errores:
            return render_template("usuarios/perfil.html", form=form)

        usuario.email = new_email
        usuario.name = new_name
        usuario.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()
        login_user(usuario)
        flash(gettext('Account updated!'), category='success')
        return redirect(url_for('main_bp.inicio'))

    return render_template("usuarios/perfil.html", form=form)


@users_bp.route('/miespacio', methods=['GET'])
@login_required
def miespacio():
    return render_template("usuarios/miespacio.html")


@users_bp.route('/datasets/<user_id>', methods=['GET'])
@login_required
def obtener_datasets(user_id):
    # Añadir comprobación para solo poder acceder a tu información
    return [json.dumps(d.to_list()) for d in Dataset.query.filter_by(user_id=user_id).all()]
