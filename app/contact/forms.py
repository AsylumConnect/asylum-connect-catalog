from flask.ext.wtf import Form
from wtforms.fields import (SelectField, StringField, SubmitField,
                            TextAreaField, TextField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired, Length


class ContactForm(Form):
    name = StringField(
        'Name', validators=[
            InputRequired(),
            Length(1, 500),
        ])
    email = EmailField(
        'Email', validators=[
            InputRequired(),
            Length(1, 500),
            Email(),
        ])
    message = TextField('Message', validators=[InputRequired()])
    submit = SubmitField('Submit')


class ContactCategoryForm(Form):
    name = StringField(
        'Name', validators=[
            InputRequired(),
            Length(1, 250),
        ])
    submit = SubmitField('Add Category')


class EditCategoryNameForm(Form):
    name = TextField(
        'Name', validators=[
            InputRequired(),
            Length(1, 250),
        ])
    submit = SubmitField('Update name')
