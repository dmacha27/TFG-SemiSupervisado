import json
import os
from functools import wraps

from flask import flash, render_template, redirect, url_for, Blueprint, request, session, jsonify, current_app, abort
from flask_login import login_user, login_required, logout_user, current_user
from flask_babel import gettext
from sqlalchemy.exc import SQLAlchemyError
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
    """
    Función que gestiona el cierre de sesión del usuario,
    elimina el algoritmo y fichero cargado de la sesión

    :return: función que redirecciona a la página de inicio.
    """

    logout_user()
    session.pop('ALGORITMO', None)
    session.pop('FICHERO', None)
    flash(gettext('Come back soon!'), category='')
    return redirect(url_for(main_bp_inicio))


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Función que gestiona el inicio de sesión del usuario.

    :returns: - función que redirecciona a la página de inicio si el inicio de sesión es correcto (POST)
              - función que genera la página de inicio de sesión (GET).
    """

    if current_user.is_authenticated:
        flash(gettext('You are already logged in!'), category='')
        return redirect(url_for(main_bp_inicio))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        email = request.form.get('email')
        password = request.form.get('password')

        usuario = User.query.filter_by(email=email).first()
        if usuario:
            if check_password_hash(usuario.password, password):
                flash(gettext('Logging successful!'), category='success')
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
    """
    Función que gestiona el registro del usuario.

    :returns: - función que redirecciona a la página de inicio si el registro es correcto (POST)
              - función que genera la página de registro si ha ocurrido algún error en el formulario (POST).
              - función que genera la página de registro (GET).
    """

    if current_user.is_authenticated:
        flash(gettext('You are already registered!'), category='')
        return redirect(url_for(main_bp_inicio))

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

        try:
            db.session.add(usuario)
        except SQLAlchemyError:
            db.session.rollback()
            flash(gettext('Could not create account!'), category='error')
            return render_template("usuarios/registro.html", form=form)
        else:
            db.session.commit()

        login_user(usuario)
        session.pop('ALGORITMO', None)
        session.pop('FICHERO', None)
        flash(gettext('Account created!'), category='success')
        return redirect(url_for(main_bp_inicio))

    return render_template("usuarios/registro.html", form=form)


@users_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """
    Función que gestiona el acceso al perfil del usuario.

    :returns: - función que redirecciona a la página de inicio.
              - función que genera la página del perfil.
    """

    return editar(current_user.id, 'main_bp.inicio')


def editar(user_id, redirect_page):
    """
    Función auxiliar que centraliza la visualización y edición de un perfil de usuario

    :param user_id: identificador del usuario.
    :param redirect_page: página de redirección.
    :returns: - función que redirecciona a la página indicada en redirect_page
              - función que genera la página del perfil.
    """

    form = UserForm(request.form)

    if current_user.is_admin:
        form.current_password.validators = []

    usuario = User.query.get(int(user_id))
    if not usuario:
        flash(gettext("User doesn't exist"), category='error')
        return redirect(url_for(redirect_page))

    n_uploads, n_runs = obtener_estadisticas_usuario(int(user_id))

    errores = False
    if request.method == 'POST' and form.validate():
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if not current_user.is_admin:
            if not check_password_hash(usuario.password, current_password):
                form.current_password.errors.append(gettext('Incorrect current password'))
                errores = True

        check_email = User.query.filter_by(email=new_email).first()
        if check_email and new_email != usuario.email:
            form.email.errors.append(gettext('Email already exists'))
            errores = True

        if errores:
            return render_template("usuarios/perfil.html",
                                   usuario=usuario,
                                   form=form,
                                   n_uploads=n_uploads,
                                   n_runs=n_runs)

        usuario.email = new_email
        usuario.name = new_name
        if new_password:
            usuario.password = generate_password_hash(new_password, method='sha256')
        db.session.commit()
        if redirect_page == 'main_bp.inicio':
            login_user(usuario)
        flash(gettext('Account updated!'), category='success')
        return redirect(url_for(redirect_page))

    return render_template("usuarios/perfil.html",
                           usuario=usuario,
                           form=form,
                           n_uploads=n_uploads,
                           n_runs=n_runs)


@users_bp.route('/miespacio', methods=['GET'])
@login_required
def miespacio():
    """
    Función que gestiona el acceso al espacio personal del usuario

    :return: función que genera la página del espacio personal.
    """

    usuario = User.query.get(int(current_user.id))
    if not usuario:
        abort(404)

    n_uploads, n_runs = obtener_estadisticas_usuario(current_user.id)

    return render_template("usuarios/miespacio.html",
                           usuario=usuario,
                           n_uploads=n_uploads,
                           n_runs=n_runs)


def obtener_estadisticas_usuario(user_id):
    """
    Función auxiliar para la obtención de las estadísticas de usuario:
        - conjuntos de datos (subidas)
        - ejecuciones previas

    :param user_id: identificador de usuario.
    :return: número de subidas y número de ejecuciones.
    """

    datasets = Dataset.query.filter_by(user_id=user_id).all()
    n_uploads = len(datasets) if datasets else 0

    runs = Run.query.filter_by(user_id=user_id).all()
    n_runs = len(runs) if runs else 0

    return n_uploads, n_runs


@users_bp.route('/datasets/obtener/<user_id>', methods=['GET'])
@login_required
def obtener_datasets(user_id):
    """
    Obtiene los conjuntos de datos subidos por un usuario

    :param user_id: identificador del usuario.
    :returns: - si el usuario no está autorizado, json con el estado, el código HTTP y el mensaje del error.
              - lista con los conjuntos de datos subidos en formato json (su información).
    """

    if int(user_id) != current_user.id and not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    return [json.dumps(d.to_list()) for d in Dataset.query.filter_by(user_id=user_id).all()]


@users_bp.route('/datasets/eliminar', methods=['DELETE'])
@login_required
def eliminar_dataset():
    """
    Elimina un conjunto de datos (base de datos y fichero en el sistema).
    Recibe en el cuerpo de la petición el identificador del usuario y el fichero
    a eliminar

    :return: json con el estado, el código HTTP y si ha ocurrido algún error, el mensaje del mismo.
    """

    json_request = request.json
    if 'id' not in json_request or 'fichero' not in json_request:
        return jsonify({
            "status": "error",
            "error": "bad request"
        }), 400

    if int(json_request['id']) != current_user.id and not current_user.is_admin:  # Solo el propio usuario o
        # administrador puede eliminar
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    try:
        Dataset.query.filter(Dataset.filename == json_request['fichero']).delete()
        db.session.commit()
        os.remove(os.path.join(current_app.config['CARPETA_DATASETS_REGISTRADOS'], json_request['fichero']))
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
    """
    Obtiene las ejecuciones previas de un usuario

    :param user_id: identificador del usuario.
    :returns: - si el usuario no está autorizado, json con el estado, el código HTTP y el mensaje del error.
              - lista con las ejecuciones previas en formato json (su información).
    """

    if int(user_id) != current_user.id and not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    return [json.dumps(h.to_list()) for h in Run.query.filter_by(user_id=user_id).all()]


@users_bp.route('/historial/eliminar', methods=['DELETE'])
@login_required
def eliminar_historial():
    """
    Elimina una ejecución previa (base de datos y fichero en el sistema)
    Recibe en el cuerpo de la petición el identificador del usuario y el fichero
    a eliminar

    :return: json con el estado, el código HTTP y si ha ocurrido algún error, el mensaje del mismo.
    """

    json_request = request.json
    if 'id' not in json_request or 'fichero' not in json_request:
        return jsonify({
            "status": "error",
            "error": "bad request"
        }), 400

    if int(json_request['id']) != current_user.id and not current_user.is_admin:
        return jsonify({
            "status": "error",
            "error": "unauthorized"
        }), 401

    try:
        Run.query.filter(Run.jsonfile == json_request['fichero']).delete()
        db.session.commit()
        os.remove(os.path.join(current_app.config['CARPETA_RUNS'], json_request['fichero']))
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

    return jsonify({
        "status": "success"}), 200


@users_bp.route('/admin', methods=['GET'])
@login_required
def admin_panel():
    """
    Función que gestiona el acceso al panel de administrador

    :return: función que genera la página.
    """

    if not current_user.is_admin:
        abort(401)

    return render_template("usuarios/admin.html")


def admin_api_required(f):
    """
    Actúa como precondición de algunas de las rutas
    comprobando que el usuario que intenta acceder es administrador

    :param f: función decorada.
    :return: decorador con la precondición.
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({
                "status": "error",
                "error": "unauthorized"
            }), 401
        return f(*args, **kwargs)

    return wrapped


@users_bp.route('/datasets/obtener', methods=['GET'])
@login_required
@admin_api_required
def obtener_datasets_todos():
    """
    Obtiene todos los conjuntos de datos subidos por todos los usuarios

    :return: lista con los conjuntos de datos subidos en formato json (su información).
    """

    return [json.dumps(d.to_list()) for d in Dataset.query.all()]


@users_bp.route('/datasets/ultimos', methods=['GET'])
@login_required
@admin_api_required
def obtener_datasets_ultimos():
    """
    Obtiene el número de conjuntos de datos subidos de todos los usuarios en los últimos 7 dias

    :return: número de conjuntos de datos.
    """

    date = datetime.today() - timedelta(days=7)

    datasets = Dataset.query.filter(Dataset.date >= date).all()

    return str(len(datasets)) if datasets else "0"


@users_bp.route('/historial/obtener', methods=['GET'])
@login_required
@admin_api_required
def obtener_historial_todos():
    """
    Obtiene todas las ejecuciones previas de todos los usuarios

    :return: lista con las ejecuciones en formato json (su información).
    """

    return [json.dumps(h.to_list()) for h in Run.query.all()]


@users_bp.route('/historial/ultimos', methods=['GET'])
@login_required
@admin_api_required
def obtener_historial_ultimos():
    """
    Obtiene el número de las ejecuciones previas de todos los usuarios en los últimos 7 dias

    :return: número de las ejecuciones previas.
    """

    date = datetime.today() - timedelta(days=7)

    runs = Run.query.filter(Run.date >= date).all()

    return str(len(runs)) if runs else "0"


@users_bp.route('/usuarios/obtener', methods=['GET'])
@login_required
@admin_api_required
def obtener_usuarios_todos():
    """
    Obtiene todos los usuarios

    :return: lista con los usuarios en formato json (su información).
    """

    return [json.dumps(u.to_list()) for u in User.query.all()]


@users_bp.route('/usuarios/eliminar', methods=['DELETE'])
@login_required
@admin_api_required
def eliminar_usuario():
    """
    Elimina un usuario. Recibe en el cuerpo de la petición el identificador del usuario.
    Se encarga de eliminar todos los conjuntos de datos y ejecuciones previas del usuario
    (tanto de la base de datos como ficheros del sistema) y finalmente, el usuario.

    :return: json con el estado, el código HTTP y si ha ocurrido algún error, el mensaje del mismo.
    """

    json_request = request.json

    try:
        # Eliminar todos los ficheros
        datasets = Dataset.query.filter(Dataset.user_id == json_request['user_id']).all()
        datasets_filenames = []
        for dataset in datasets:
            datasets_filenames.append(dataset.filename)
            db.session.delete(dataset)

        runs = Run.query.filter(Run.user_id == json_request['user_id']).all()
        runs_filenames = []
        for run in runs:
            runs_filenames.append(run.jsonfile)
            db.session.delete(run)

        User.query.filter(User.id == json_request['user_id']).delete()
        db.session.commit()

        for filename in datasets_filenames:
            os.remove(os.path.join(current_app.config['CARPETA_DATASETS_REGISTRADOS'], filename))

        for filename in runs_filenames:
            os.remove(os.path.join(current_app.config['CARPETA_RUNS'], filename))

    except SQLAlchemyError as se:
        db.session.rollback()
        return jsonify({
            "status": "database error",
            "error": str(se)
        }), 500
    except Exception as e:
        return jsonify({
            "status": "critical error",
            "error": str(e)
        }), 500

    return jsonify({
        "status": "success"}), 200


def user_id_int(f):
    """
    Actúa como precondición para asegurar un
    identificador convertible a entero.

    :param f: función decorada.
    :return: decorador con la precondición.
    """

    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            _ = int(request.view_args.get('user_id', None))
        except ValueError:
            abort(400)
        return f(*args, **kwargs)

    return wrapped


@users_bp.route('/admin/usuario/editar/<user_id>', methods=['GET', 'POST'])
@login_required
@user_id_int
def admin_editar_usuario(user_id):
    """
    Función que gestiona la edición de un usuario por parte de un
    administrador

    :param user_id: identificador del usuario.
    :returns: - función que redirecciona a la página de administración.
              - función que genera la página del perfil.
    """

    if not current_user.is_admin:
        abort(401)

    return editar(user_id, 'users_bp.admin_panel')
