from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, ValidationError, Optional
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, DateField, SelectField, HiddenField, SubmitField
from wtforms_alchemy import model_form_factory
from models import User, PRIORITY_LEVELS, STATUSES

BaseModelForm = model_form_factory(FlaskForm)


password_validators = [
    DataRequired(),
    Length(min=8, max=50),
    Regexp(r".*\d.*"),
    Regexp(r".*[a-z].*"),
    Regexp(r".*[A-Z].*"),
    Regexp(r'.*[!@#$%^&*(),.?":{}|<>].*')
]


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=password_validators)


class RegisterForm(LoginForm):
    confirmation = PasswordField('Password Confirmation', validators=[DataRequired(), EqualTo('password')])


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=password_validators)
    confirmation = PasswordField('Confirm new password', validators=[DataRequired(), EqualTo('password')])


class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField("Description")
    assignee = StringField('Assignee', validators=[DataRequired()])
    due_date = DateField('Due date', validators=[DataRequired()])
    priority_id = SelectField('Priority', choices=list(enumerate(PRIORITY_LEVELS)))


class EditTaskForm(TaskForm):
    id = HiddenField('id', validators=[DataRequired()])
    status_id = SelectField('Status', choices=list(enumerate(STATUSES)))


class SearchTaskForm(FlaskForm):
    text = TextAreaField('Text')
    assignee = StringField('Assignee')
    assigner = StringField('Assigner')
    due_date = DateField('Due date', validators=[Optional()])
    priority_id = SelectField('Priority', choices=[("Any", "Any")] + list(enumerate(PRIORITY_LEVELS)))
    status_id = SelectField('Status', choices=[("Any", "Any")] + list(enumerate(STATUSES)))


class CommentForm(FlaskForm):
    text = TextAreaField("Your comment", validators=[DataRequired()])
    task_id = HiddenField('Task id', validators=[DataRequired()])