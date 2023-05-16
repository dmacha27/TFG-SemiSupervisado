from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import (StringField, EmailField, PasswordField, SelectField, IntegerField, DecimalField, BooleanField,
                     IntegerRangeField)
from wtforms.validators import (DataRequired, InputRequired, Length, EqualTo, NumberRange)


class RegistrationForm(FlaskForm):
    name = StringField(lazy_gettext('Name'),
                       name="name",
                       id="name",
                       validators=[DataRequired(), Length(min=2, max=10)],
                       render_kw={"placeholder": lazy_gettext('Name')})

    email = EmailField(lazy_gettext('Email'),
                       name="email",
                       id="email",
                       validators=[DataRequired()],
                       render_kw={"placeholder": lazy_gettext('Email')})

    password = PasswordField(lazy_gettext('Password'),
                             name="password",
                             id="password",
                             validators=[DataRequired(), Length(min=8)],
                             render_kw={"placeholder": lazy_gettext('Password')})

    confirm_password = PasswordField(lazy_gettext('Confirm password'),
                                     name="confirm_password",
                                     id="confirm_password",
                                     validators=[DataRequired(), EqualTo('password')],
                                     render_kw={"placeholder": lazy_gettext('Password')})


class LoginForm(FlaskForm):
    email = EmailField(lazy_gettext('Email'), validators=[DataRequired()],
                       render_kw={"placeholder": lazy_gettext('Email')})

    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()],
                             render_kw={"placeholder": lazy_gettext('Password')})


class UserForm(FlaskForm):
    name = StringField(lazy_gettext('Name'),
                       name="name",
                       id="name",
                       validators=[Length(min=2, max=10)],
                       render_kw={"placeholder": lazy_gettext('Name')})

    email = EmailField(lazy_gettext('Email'),
                       name="email",
                       id="email",
                       render_kw={"placeholder": lazy_gettext('Email')})

    current_password = PasswordField(lazy_gettext('Current password'),
                                     name="current_password",
                                     id="current_password",
                                     validators=[DataRequired(), Length(min=8)],
                                     render_kw={"placeholder": lazy_gettext('Current password')})

    new_password = PasswordField(lazy_gettext('New password'),
                                 name="new_password",
                                 id="new_password",
                                 validators=[Length(min=8)],
                                 render_kw={"placeholder": lazy_gettext('New password')})


class FormConfiguracionBase(FlaskForm):
    sel_target = SelectField(lazy_gettext('Select the target/class attribute of the dataset'),
                             name="target",
                             id="sel_target",
                             validators=[InputRequired()])

    cx = SelectField(lazy_gettext('Select X component'),
                     name="cx",
                     id="cx",
                     validators=[InputRequired()])

    cy = SelectField(lazy_gettext('Select Y component'),
                     name="cy",
                     id="cy",
                     validators=[InputRequired()])

    pca = BooleanField(lazy_gettext('Use PCA to reduce to 2D'),
                       name="pca",
                       id="pca")

    stand = BooleanField(lazy_gettext('Standardize'),
                         name="stand",
                         id="stand")

    p_unlabelled = IntegerRangeField(lazy_gettext('Unlabelled percentage'),
                                     name="p_unlabelled",
                                     id="p_unlabelled",
                                     default=80,
                                     validators=[InputRequired(), NumberRange(min=1, max=99)])

    p_test = IntegerRangeField(lazy_gettext('Test percentage (after unlabelled percentage)'),
                               name="p_test",
                               id="p_test",
                               default=20,
                               validators=[InputRequired(), NumberRange(min=1, max=99)])


class FormConfiguracionSelfTraining(FormConfiguracionBase):
    clasificador1 = SelectField(lazy_gettext('Select classifier'),
                                name="clasificador1",
                                id="clasificador1",
                                validators=[InputRequired()])

    n = IntegerField(lazy_gettext('N (Number of instances to select in each iteration)'),
                     name="n",
                     id="n",
                     default=10,
                     validators=[InputRequired(), NumberRange(min=1)])

    th = DecimalField(lazy_gettext('Threshold'),
                      name="th",
                      id="th",
                      validators=[InputRequired(), NumberRange(min=0, max=0.99)])

    n_iter = IntegerField(lazy_gettext('Number of iterations'),
                          name="n_iter",
                          id="n_iter",
                          default=10,
                          validators=[InputRequired(), NumberRange(min=0)])


class FormConfiguracionCoTraining(FormConfiguracionBase):
    clasificador1 = SelectField(lazy_gettext('Select classifier'),
                                name="clasificador1",
                                id="clasificador1",
                                validators=[InputRequired()])

    clasificador2 = SelectField(lazy_gettext('Select classifier'),
                                name="clasificador2",
                                id="clasificador2",
                                validators=[InputRequired()])

    p = IntegerField(lazy_gettext('Positives') + " (p)",
                     name="p",
                     id="n",
                     default=1,
                     validators=[InputRequired(), NumberRange(min=0)])

    n = IntegerField(lazy_gettext('Negatives') + " (n)",
                     name="n",
                     id="n",
                     default=3,
                     validators=[InputRequired(), NumberRange(min=0)])

    u = IntegerField(lazy_gettext('Number of initial data'),
                     name="u",
                     id="u",
                     default=75,
                     validators=[InputRequired(), NumberRange(min=1)])

    n_iter = IntegerField(lazy_gettext('Number of iterations'),
                          name="n_iter",
                          id="n_iter",
                          default=30,
                          validators=[InputRequired(), NumberRange(min=0)])


class FormConfiguracionSingleView(FormConfiguracionBase):
    clasificador1 = SelectField(lazy_gettext('Select classifier'),
                                name="clasificador1",
                                id="clasificador1",
                                validators=[InputRequired()])

    clasificador2 = SelectField(lazy_gettext('Select classifier'),
                                name="clasificador2",
                                id="clasificador2",
                                validators=[InputRequired()])

    clasificador3 = SelectField(lazy_gettext('Select classifier'),
                                name="clasificador3",
                                id="clasificador3",
                                validators=[InputRequired()])
