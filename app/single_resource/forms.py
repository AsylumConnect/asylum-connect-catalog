from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class SingleResourceForm(Form):
    name = StringField(
        'Resource Name', validators=[InputRequired(), Length(1, 512)])
    address = StringField('Address', validators=[])
    latitude = StringField('Latitude', validators=[])
    longitude = StringField('Longitude', validators=[])
    submit = SubmitField('Save Resource')
