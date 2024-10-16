from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, validators, PasswordField


class LoginForm(FlaskForm):
    email = EmailField('Email', [validators.DataRequired("Please enter your email address."),
                                 validators.Email("Please enter your email address.")],
                       render_kw={"placeholder": "Email"})
    password = PasswordField('Password',
                             validators=[validators.DataRequired(message="You need to provide password")],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


class SignInForm(FlaskForm):
    user_name = StringField("Username", render_kw={"placeholder": "Username"}, validators=[validators.DataRequired()])
    email = EmailField('Email', [validators.DataRequired("Please enter your email address."),
                                 validators.Email("Please enter your email address.")],
                       render_kw={"placeholder": "Email"})
    password = PasswordField('Password',
                             validators=[validators.DataRequired(message="You need to provide password")],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField("Sign Up")
