"""Formulários WTForms da área administrativa."""

from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class UserCreateForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired(), Length(min=2, max=50)])
    sector = SelectField("Setor", choices=[], validators=[DataRequired()])
    role = SelectField("Role", choices=[("ADMIN", "ADMIN"), ("RH", "RH"), ("USER", "USER")], validators=[DataRequired()])
    password = PasswordField("Senha inicial", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Criar")


class UserEditForm(FlaskForm):
    user_id = HiddenField(validators=[DataRequired()])
    sector = SelectField("Setor", choices=[], validators=[DataRequired()])
    role = SelectField("Role", choices=[("ADMIN", "ADMIN"), ("RH", "RH"), ("USER", "USER")], validators=[DataRequired()])
    submit = SubmitField("Salvar")


class PasswordResetForm(FlaskForm):
    user_id = HiddenField(validators=[DataRequired()])
    password = PasswordField("Nova senha", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Resetar")


class EmergencyForm(FlaskForm):
    room_id = SelectField("Sala", choices=[], validators=[DataRequired()])
    date = StringField("Data (YYYY-MM-DD)", validators=[DataRequired()])
    start_time = StringField("Início (HH:MM)", validators=[DataRequired()])
    end_time = StringField("Fim (HH:MM)", validators=[DataRequired()])
    reason = TextAreaField("Motivo", validators=[DataRequired(), Length(min=3, max=500)])
    submit = SubmitField("Criar emergência")


class DecisionForm(FlaskForm):
    request_ids = HiddenField(validators=[DataRequired()])
    reason = StringField("Motivo", validators=[Optional(), Length(max=200)])
    submit_approve = SubmitField("Aprovar lote")
    submit_deny = SubmitField("Recusar lote")


class BookingCancelForm(FlaskForm):
    booking_id = HiddenField(validators=[DataRequired()])
    reason = StringField("Motivo", validators=[Optional(), Length(max=200)])
    submit = SubmitField("Cancelar")
