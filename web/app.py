import os
import json

import pandas as pd
from flask import Flask, flash, render_template, request, redirect, session
from flask_session import Session
from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.svm import SVC
from werkzeug.utils import secure_filename

from algoritmos import SelfTraining
from algoritmos import CoTraining
from algoritmos.utilidades import DatasetLoader, log_pca_reduction, log_cxcy_reduction

app = Flask(__name__)
app.secret_key = "secreta"
app.config.update(SESSION_COOKIE_SAMESITE='Strict')
app.config['CARPETA_DATASETS'] = 'datasets'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/', methods=['GET'])
def inicio():
    session.pop('ALGORITMO', None)
    session.pop('FICHERO', None)
    return render_template('inicio.html')


@app.route('/sel_selftraining')
def sel_selftraining():
    session['ALGORITMO'] = 'selftraining'
    return redirect('/subida')


@app.route('/sel_cotraining')
def sel_cotraining():
    session['ALGORITMO'] = 'cotraining'
    return redirect('/subida')


@app.route('/subida', methods=['GET', 'POST'])
def subida():
    if 'ALGORITMO' not in session:
        flash("Debe seleccionar un algoritmo")
        return redirect('/')

    if request.method == 'POST':
        file = request.files['archivo']
        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            session['FICHERO'] = os.path.join(app.config['CARPETA_DATASETS'], filename)
            file.save(os.path.join(app.config['CARPETA_DATASETS'], filename))

    return render_template('subida.html')


@app.route('/selftrainingc', methods=['GET'])
def configuracionselftraining():
    if 'FICHERO' not in session:
        flash("Debe subir un fichero")
        return redirect('/subida')

    dl = DatasetLoader(session['FICHERO'])
    return render_template('selftrainingconfig.html', caracteristicas=dl.features())


@app.route('/cotrainingc', methods=['GET'])
def configuracioncotraining():
    if 'FICHERO' not in session:
        flash("Debe subir un fichero")
        return redirect('/subida')

    dl = DatasetLoader(session['FICHERO'])
    return render_template('cotrainingconfig.html', caracteristicas=dl.features())


@app.route('/selftraining', methods=['GET', 'POST'])
def selftraining():
    if 'target' not in request.form:
        flash("Debe seleccionar los parámetros del algoritmo")
        return redirect('/selftrainingc')

    return render_template('selftraining.html',
                           n=request.form['n'] if 'n' in request.form else -1,
                           th=request.form['th'] if 'th' in request.form else -1,
                           n_iter=request.form['n_iter'],
                           target=request.form['target'],
                           cx=request.form['cx'] if 'cx' in request.form else 'C1',
                           cy=request.form['cy'] if 'cy' in request.form else 'C2',
                           pca=request.form['pca'] if 'pca' in request.form else 'off')


@app.route('/cotraining', methods=['GET', 'POST'])
def cotraining():
    if 'target' not in request.form:
        flash("Debe seleccionar los parámetros del algoritmo")
        return redirect('/cotrainingc')

    return render_template('cotraining.html',
                           p=request.form['p'] if 'p' in request.form else -1,
                           n=request.form['n'] if 'n' in request.form else -1,
                           u=request.form['u'] if 'u' in request.form else -1,
                           n_iter=request.form['n_iter'],
                           target=request.form['target'],
                           cx=request.form['cx'] if 'cx' in request.form else 'C1',
                           cy=request.form['cy'] if 'cy' in request.form else 'C2',
                           pca=request.form['pca'] if 'pca' in request.form else 'off')


@app.route('/selftrainingd', methods=['GET', 'POST'])
def datosselftraining():
    n = int(request.form['n'])
    th = float(request.form['th'])
    n_iter = int(request.form['n_iter'])
    cx = request.form['cx']
    cy = request.form['cy']
    pca = request.form['pca']
    clf = SVC(kernel='rbf',
              probability=True,
              C=1.0,
              gamma='scale',
              random_state=0
              )

    st = SelfTraining(clf=clf,
                      n=n if n != -1 else None,
                      th=th if th != -1 else None,
                      n_iter=n_iter)

    dl = DatasetLoader(session['FICHERO'])
    dl.set_target(request.form['target'])
    x, y, mapa, _ = dl.get_x_y()
    log, it = st.fit(x, y)

    if pca == 'on':
        _2d = log_pca_reduction(log).to_json()
    else:
        _2d = log_cxcy_reduction(log, cx, cy).to_json()

    info = {'log': _2d,
            'mapa': json.dumps(mapa)}

    return json.dumps(info)


@app.route('/cotrainingd', methods=['GET', 'POST'])
def datoscotraining():
    p = int(request.form['p'])
    n = int(request.form['n'])
    u = int(request.form['u'])
    n_iter = int(request.form['n_iter'])
    cx = request.form['cx']
    cy = request.form['cy']
    pca = request.form['pca']

    clf1 = SVC(kernel='rbf',
               probability=True,
               C=1.0,
               gamma='scale',
               random_state=0
               )
    clf2 = SVC(kernel='rbf',
               probability=True,
               C=1.0,
               gamma='scale',
               random_state=0
               )

    ct = CoTraining(clf1=clf1,
                    clf2=clf2,
                    p=p,
                    n=n,
                    u=u,
                    n_iter=n_iter)

    dl = DatasetLoader(session['FICHERO'])
    dl.set_target(request.form['target'])
    x, y, mapa, _ = dl.get_x_y()
    log, it = ct.fit(x, y)

    if pca == 'on':
        _2d = log_pca_reduction(log).to_json()
    else:
        _2d = log_cxcy_reduction(log, cx, cy).to_json()

    info = {'log': _2d,
            'mapa': json.dumps(mapa)}
    return json.dumps(info)


if __name__ == '__main__':
    app.run(debug=True)
