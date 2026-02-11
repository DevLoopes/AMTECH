"""Formulários WTForms do fluxo de autenticação."""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=3, max=128)])
    submit = SubmitField("Entrar")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Senha atual", validators=[DataRequired()])
    new_password = PasswordField("Nova senha", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Alterar senha")
