from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import (StringField, EmailField, PasswordField)
from wtforms.validators import (DataRequired, Length, EqualTo)


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
                             validators=[DataRequired()],
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

    actual_password = PasswordField(lazy_gettext('Actual password'),
                                    name="actual_password",
                                    id="actual_password",
                                    validators=[DataRequired()],
                                    render_kw={"placeholder": lazy_gettext('Actual password')})

    new_password = PasswordField(lazy_gettext('New password'),
                                 name="new_password",
                                 id="new_password",
                                 render_kw={"placeholder": lazy_gettext('New password')})
