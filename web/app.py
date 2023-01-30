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
from algoritmos.utilidades import DatasetLoader
from algoritmos.utilidades import log_dim_reduction

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

    return render_template('subida.html', alg=session['ALGORITMO'])


@app.route('/selftrainingc', methods=['GET'])
def configuracionselftraining():
    if 'FICHERO' not in session:
        flash("Debe subir un fichero")
        return redirect('/subida')
    dl = DatasetLoader(session['FICHERO'])
    return render_template('selftrainingconfig.html', caracteristicas=dl.features())


@app.route('/selftraining', methods=['GET', 'POST'])
def selftraining():
    if 'target' not in request.form:
        flash("Debe seleccionar los parámetros del algoritmo")
        return redirect('/selftrainingc')

    return render_template('selftraining.html',
                           n=request.form['n'] if 'n' in request.form else -1,
                           th=request.form['th'] if 'th' in request.form else -1,
                           n_iter=request.form['n_iter'],
                           target=request.form['target'])


@app.route('/selftrainingd', methods=['GET', 'POST'])
def datosselftraining():
    n = int(request.form['n'])
    th = float(request.form['th'])
    n_iter = int(request.form['n_iter'])
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

    info = {'log': log_dim_reduction(log).to_json(),
            'mapa': json.dumps(mapa)}

    return json.dumps(info)


@app.route('/cotrainingd', methods=['GET'])
def datoscotraining():
    data = load_breast_cancer()
    x = pd.DataFrame(data['data'], columns=data['feature_names'])
    y = pd.DataFrame(data['target'], columns=['target'])

    st = CoTraining(clf1=SVC(kernel='rbf',
                             probability=True,
                             C=1.0,
                             gamma='scale',
                             random_state=0
                             ),
                    clf2=SVC(kernel='rbf',
                             probability=True,
                             C=1.0,
                             gamma='scale',
                             random_state=0
                             ), p=1, n=3, u=30, n_iter=100)

    log, it = st.fit(x, y)
    return log_dim_reduction(log).to_json()


if __name__ == '__main__':
    app.run(debug=True)
