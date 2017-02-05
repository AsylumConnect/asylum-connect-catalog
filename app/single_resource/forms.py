from flask.ext.wtf import Form
from wtforms.fields import HiddenField, StringField, SubmitField
from wtforms.validators import InputRequired, Length


class SingleResourceForm(Form):
    name = StringField('Name', validators=[InputRequired(), Length(1, 512)])
    address = StringField(
        'Address', validators=[InputRequired(), Length(1, 512)])
    latitude = HiddenField('Latitude', validators=[InputRequired()])
    longitude = HiddenField('Longitude', validators=[InputRequired()])
    submit = SubmitField('Save Resource')
