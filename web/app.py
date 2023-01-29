import os

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from werkzeug.utils import secure_filename

from algoritmos import SelfTraining
from algoritmos import CoTraining
from algoritmos.utilidades.dimreduction import log_dim_reduction

app = Flask(__name__)
app.config['CARPETA_DATASETS'] = 'datasets'


@app.route('/selftraining', methods=['GET', 'POST'])
def selftraining():
    return render_template('selftraining.html', n=request.form['n'],
                           th=request.form['th'], n_iter=request.form['n_iter'])


@app.route('/', methods=['GET'])
def inicio():
    return render_template('inicio.html')


@app.route('/subida', methods=['GET', 'POST'])
def subida():
    if request.method == 'POST':

        file = request.files['archivo']
        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            session['FICHERO'] = filename
            file.save(os.path.join(app.config['CARPETA_DATASETS'], filename))

    return render_template('subida.html')


@app.route('/configuracion', methods=['GET'])
def configuracion():
    return render_template('configuracion.html')


@app.route('/selftrainingd', methods=['GET', 'POST'])
def datosselftraining():
    n = int(request.form['n'])
    th = int(request.form['th'])
    n_iter = int(request.form['n_iter'])

    data = load_breast_cancer()
    x = pd.DataFrame(data['data'], columns=data['feature_names'])
    y = pd.DataFrame(data['target'], columns=['target'])

    st = SelfTraining(clf=SVC(kernel='rbf',
                              probability=True,
                              C=1.0,
                              gamma='scale',
                              random_state=0
                              ), n=n, n_iter=n_iter)

    log, it = st.fit(x, y)
    return log_dim_reduction(log).to_json()


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
