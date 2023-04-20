import os
from datetime import datetime

from flask import flash, render_template, request, redirect, session, url_for, send_file, Blueprint, current_app
from flask_babel import gettext
from flask_login import current_user
from werkzeug.utils import secure_filename

from . import db
from .models import Dataset

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/', methods=['GET'])
def inicio():
    session.pop('ALGORITMO', None)
    return render_template('inicio.html')


@main_bp.route('/seleccionar/<algoritmo>')
def seleccionar_algoritmo(algoritmo=None):
    session['ALGORITMO'] = algoritmo
    return redirect(url_for('main_bp.subida'))


@main_bp.route('/descargar_prueba')
def descargar_prueba():
    path = 'datasets/seleccionar/Prueba.arff'
    return send_file(path, as_attachment=True)


@main_bp.route('/subida', methods=['GET', 'POST'])
def subida():
    if 'ALGORITMO' not in session:
        flash(gettext("You must select an algorithm"))
        return redirect(url_for('main_bp.inicio'))

    ya_hay_fichero = False
    if 'FICHERO' in session:
        ya_hay_fichero = True

    if request.method == 'POST':
        file_received = request.files['archivo']
        if file_received.filename == '':
            return redirect(request.url)
        if file_received:
            filename = secure_filename(file_received.filename) + "-" + str(int(datetime.now().timestamp()))
            session['FICHERO'] = os.path.join(current_app.config['CARPETA_DATASETS'], filename)
            complete_path = os.path.join(current_app.config['CARPETA_DATASETS'], filename)
            file_received.save(complete_path)

            # Si está logeado, se puede guardar el fichero en base de datos
            if current_user.is_authenticated:
                dataset = Dataset()
                dataset.filename = filename
                dataset.complete_path = complete_path
                dataset.date = datetime.now()
                dataset.user_id = current_user.id
                db.session.add(dataset)
                db.session.commit()

    return render_template('subida.html', ya_hay_fichero=ya_hay_fichero)
