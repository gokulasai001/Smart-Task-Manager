from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Optional
from .models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('Employee','Employee'),('Manager','Manager')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(max=140)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Save Project')

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired(), Length(max=140)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    status = SelectField('Status', choices=[
        ('Pending','Pending'),
        ('In Progress','In Progress'),
        ('Completed','Completed')
    ])
    priority = SelectField('Priority', choices=[
        ('Low','Low'),
        ('Medium','Medium'),
        ('High','High')
    ])
    due_date = DateField('Due Date', validators=[Optional()])
    assigned_to = SelectField('Assign To', coerce=int)
    project_id = SelectField('Project', coerce=int)
    submit = SubmitField('Save Task')