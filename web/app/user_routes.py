import json
import os

from flask import flash, render_template, redirect, url_for, Blueprint, request, session, jsonify, current_app, abort
from flask_login import login_user, login_required, logout_user, current_user
from flask_babel import gettext
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime, timedelta
from .models import User, Dataset, Run
from . import db
from .forms import RegistrationForm, LoginForm, UserForm

users_bp = Blueprint('users_bp', __name__)

main_bp_inicio = 'main_bp.inicio'


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for(main_bp_inicio))


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
                db.session.commit()
                login_user(usuario)
                session.pop('ALGORITMO', None)
                session.pop('FICHERO', None)
                return redirect(url_for(main_bp_inicio))
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
        return redirect(url_for(main_bp_inicio))

    return render_template("usuarios/registro.html", form=form)


@users_bp.route('/perfil/<user_id>', defaults={'redirect_page': 'main_bp.inicio'}, methods=['GET', 'POST'])
@users_bp.route('/perfil/<user_id>/<redirect_page>', methods=['GET', 'POST'])
@login_required
def editar(user_id, redirect_page):
    if int(user_id) != current_user.id and not current_user.is_admin:
        abort(401)

    form = UserForm(request.form)

    usuario = User.query.get(int(user_id))
    if not usuario:
        flash(gettext("User doesn't exist"), category='error')
        return redirect(url_for(redirect_page))

    errores = False
    if request.method == 'POST' and form.validate():
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if not check_password_hash(usuario.password, current_password):
            form.current_password.errors.append(gettext('Incorrect current password'))
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
        if redirect_page == 'main_bp.inicio':
            login_user(usuario)
        flash(gettext('Account updated!'), category='success')
        return redirect(url_for(redirect_page))

    n_uploads, n_runs = obtener_estadisticas_usuario(int(user_id))

    return render_template("usuarios/perfil.html",
                           usuario=usuario,
                           form=form,
                           n_uploads=n_uploads,
                           n_runs=n_runs)


@users_bp.route('/miespacio/<user_id>', methods=['GET'])
@login_required
def miespacio(user_id):
    if int(user_id) != current_user.id and not current_user.is_admin:
        abort(401)

    usuario = User.query.get(int(user_id))
    if not usuario:
        abort(404)

    n_uploads, n_runs = obtener_estadisticas_usuario(user_id)

    return render_template("usuarios/miespacio.html",
                           usuario=usuario,
                           n_uploads=n_uploads,
                           n_runs=n_runs)


def obtener_estadisticas_usuario(user_id):
    datasets = Dataset.query.filter_by(user_id=user_id).all()
    n_uploads = len(datasets) if datasets else 0

    runs = Run.query.filter_by(user_id=user_id).all()
    n_runs = len(runs) if runs else 0

    return n_uploads, n_runs


@users_bp.route('/datasets/obtener/<user_id>', methods=['GET'])
@login_required
def obtener_datasets(user_id):
    if int(user_id) != current_user.id and not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    return [json.dumps(d.to_list()) for d in Dataset.query.filter_by(user_id=user_id).all()]


@users_bp.route('/datasets/eliminar', methods=['POST'])
@login_required
def eliminar_dataset():
    json_request = request.json
    if int(json_request['id']) != current_user.id and not current_user.is_admin:  # Solo el propio usuario o
        # administrador puede eliminar
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    try:
        Dataset.query.filter(Dataset.filename == json_request['fichero']).delete()
        db.session.commit()
        os.remove(os.path.join(current_app.config['CARPETA_DATASETS'], json_request['fichero']))
        session.pop('ALGORITMO', None)
        session.pop('FICHERO', None)
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

    return jsonify({
        "status": "success"}), 200


@users_bp.route('/historial/obtener/<user_id>', methods=['GET'])
@login_required
def obtener_historial(user_id):
    if int(user_id) != current_user.id and not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    return [json.dumps(h.to_list()) for h in Run.query.filter_by(user_id=user_id).all()]


@users_bp.route('/admin', methods=['GET'])
@login_required
def admin_panel():
    if not current_user.is_admin:
        abort(401)

    return render_template("usuarios/admin.html")


@users_bp.route('/datasets/obtener', methods=['GET'])
@login_required
def obtener_datasets_todos():
    if not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    return [json.dumps(d.to_list()) for d in Dataset.query.all()]


@users_bp.route('/datasets/ultimos', methods=['GET'])
@login_required
def obtener_datasets_ultimos():
    if not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    date = datetime.today() - timedelta(days=7)

    datasets = Dataset.query.filter(Dataset.date >= date).all()

    return str(len(datasets)) if datasets else "0"


@users_bp.route('/historial/obtener', methods=['GET'])
@login_required
def obtener_historial_todos():
    if not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    return [json.dumps(h.to_list()) for h in Run.query.all()]


@users_bp.route('/historial/ultimos', methods=['GET'])
@login_required
def obtener_historial_ultimos():
    if not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    date = datetime.today() - timedelta(days=7)

    runs = Run.query.filter(Run.date >= date).all()

    return str(len(runs)) if runs else "0"


@users_bp.route('/usuarios/obtener', methods=['GET'])
@login_required
def obtener_usuarios_todos():
    if not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    return [json.dumps(u.to_list()) for u in User.query.all()]


@users_bp.route('/usuarios/eliminar', methods=['POST'])
@login_required
def eliminar_usuario():
    json_request = request.json
    if not current_user.is_admin:  # Solo el administrador puede eliminar
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    try:
        User.query.filter(User.id == json_request['user_id']).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

    return jsonify({
        "status": "success"}), 200


@users_bp.route('/admin/usuario/editar/<user_id>', methods=['GET', 'POST'])
@login_required
def admin_editar_usuario(user_id):
    if not current_user.is_admin:
        abort(401)

    return editar(user_id, 'users_bp.admin_panel')
