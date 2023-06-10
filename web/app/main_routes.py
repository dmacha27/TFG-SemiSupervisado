import os
from datetime import datetime

from flask import flash, render_template, request, redirect, session, url_for, send_file, Blueprint, current_app, abort
from flask_babel import gettext
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from . import db
from .models import Dataset

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/', methods=['GET'])
def inicio():
    """
    Renderiza la página de inicio

    :return: función que genera la página.
    """

    session.pop('ALGORITMO', None)
    return render_template('inicio.html')


@main_bp.route('/seleccionar/<algoritmo>', methods=['GET'])
def seleccionar_algoritmo(algoritmo):
    """
    Guarda en la sesión el algoritmo seleccionado y redirecciona
    a la página de carga del conjunto de datos

    :param algoritmo: nombre del algoritmo seleccionado.
    :return: función de redirección a la carga del conjunto de datos.
    """

    if algoritmo not in current_app.config['ALGORITMOS_SELECCIONABLES']:
        abort(404)
    session['ALGORITMO'] = algoritmo
    return redirect(url_for('main_bp.subida'))


@main_bp.route('/seleccionar/<algoritmo>/<fichero>', methods=['GET'])
@login_required
def seleccionar_algoritmo_ejecutar(algoritmo, fichero):
    """
    Permite seleccionar un algoritmo a ejecutar utilizando un conjunto
    de datos ya almacenado como fichero

    :param algoritmo: nombre del algoritmo.
    :param fichero: nombre del fichero.
    :return: función de redirección a la configuración del algoritmo.
    """

    if algoritmo not in current_app.config['ALGORITMOS_SELECCIONABLES']:
        abort(404)

    dataset = Dataset.query.filter(Dataset.filename == fichero).first()
    if not dataset:
        abort(404)

    if dataset.user_id != current_user.id:
        abort(401)

    session['ALGORITMO'] = algoritmo
    session['FICHERO'] = os.path.join(current_app.config['CARPETA_DATASETS_REGISTRADOS'], fichero)
    return redirect(url_for('configuration_bp.configurar_algoritmo', algoritmo=algoritmo))


@main_bp.route('/descargar_prueba')
def descargar_prueba():
    """
    Gestiona la descarga de un fichero de prueba (en la carga del conjunto de datos).

    :return: fichero de prueba.
    """

    path = 'datasets/seleccionar/Prueba.arff'
    return send_file(path, as_attachment=True)


@main_bp.route('/subida', methods=['GET', 'POST'])
def subida():
    """
    Gestiona la carga del conjunto de datos. Detecta en la sesión ya
    existía un fichero y realiza el formateo del nombre del fichero mediante
    el "timestamp" para hacerlo único. Finalmente, guarda este fichero en el sistema
    y lo enlaza, si corresponde, al usuario en base de datos

    :return: :return: función que genera la página.
    """

    if 'ALGORITMO' not in session:
        flash(gettext("You must select an algorithm"), category='error')
        return redirect(url_for('main_bp.inicio'))

    ya_hay_fichero = False
    if 'FICHERO' in session:
        if os.path.exists(session['FICHERO']):
            ya_hay_fichero = True
        else:
            session.pop('FICHERO', None)

    if request.method == 'POST':
        file_received = request.files['archivo']
        if file_received.filename == '':
            return redirect(request.url)
        if file_received:
            filename = secure_filename(file_received.filename) + "-" + str(int(datetime.now().timestamp()))
            if current_user.is_authenticated:
                complete_path = os.path.join(current_app.config['CARPETA_DATASETS_REGISTRADOS'], filename)
                session['FICHERO'] = complete_path
            else:
                complete_path = os.path.join(current_app.config['CARPETA_DATASETS_ANONIMOS'], filename)
                session['FICHERO'] = complete_path

            if file_received.filename.upper().endswith('.ARFF') or file_received.filename.upper().endswith('.CSV'):
                file_received.save(complete_path)

                # Si está logeado, se puede guardar el fichero en base de datos
                if current_user.is_authenticated:
                    dataset = Dataset()
                    dataset.filename = filename
                    dataset.date = datetime.now()
                    dataset.user_id = current_user.id
                    db.session.add(dataset)
                    db.session.commit()

    return render_template('subida.html', ya_hay_fichero=ya_hay_fichero)
