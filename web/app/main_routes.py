import os
import sys
import datetime

from flask import Flask, flash, render_template, request, redirect, session, url_for, send_file, Blueprint, current_app
from flask_babel import gettext
from werkzeug.utils import secure_filename

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/', methods=['GET'])
def inicio():
    session.pop('ALGORITMO', None)
    session.pop('FICHERO', None)
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

    if request.method == 'POST':
        file = request.files['archivo']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename) + "-" + str(int(datetime.datetime.now().timestamp()))
            session['FICHERO'] = os.path.join(current_app.config['CARPETA_DATASETS'], filename)
            file.save(os.path.join(current_app.config['CARPETA_DATASETS'], filename))

    return render_template('subida.html')
