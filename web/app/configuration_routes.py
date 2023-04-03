import json
import os
import sys

from flask import Flask, flash, render_template, redirect, session, url_for, Blueprint
from flask_babel import gettext

from algoritmos.utilidades.datasetloader import DatasetLoader

configuration_bp = Blueprint('configuration_bp', __name__)


@configuration_bp.route('/<algoritmo>', methods=['GET'])
def configurar_algoritmo(algoritmo=None):
    if 'FICHERO' not in session:
        flash(gettext("You must upload a file"))
        return redirect(url_for('main_bp.subida'))

    if '.ARFF' not in session['FICHERO'].upper():
        if '.CSV' not in session['FICHERO'].upper():
            flash(gettext("File must be ARFF or CSV"))
            return redirect(url_for('main_bp.subida'))

    dl = DatasetLoader(session['FICHERO'])
    with open(os.path.join(os.path.dirname(__file__), os.path.normpath("static/json/parametros.json"))) as f:
        clasificadores = json.load(f)

    return render_template('configuracion/' + algoritmo + 'config.html',
                           caracteristicas=dl.get_allfeatures(),
                           clasificadores=list(clasificadores.keys()),
                           parametros=clasificadores)
