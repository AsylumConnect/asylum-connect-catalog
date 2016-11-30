from flask.ext.wtf import Form
from wtforms.fields import FloatField, StringField, SubmitField
from wtforms.validators import Email, InputRequired, Length


class ResourceSuggestionForm(Form):
    name = StringField(
        'Name',
        validators=[InputRequired(), Length(1, 512)]
    )
    address = StringField(
        'Address', validators=[InputRequired(), Length(1, 512)]
    )
    latitude = FloatField(
        'Latitude',
        validators=[InputRequired()]
    )
    longitude = FloatField(
        'Longitude',
        validators=[InputRequired()]
    )
    notes = StringField(
        'Notes'
    )
    contact_name = StringField(
        'Contact Name',
        validators=[InputRequired(), Length(1, 512)]
    )
    contact_email = StringField(
        'Email',
        validators=[InputRequired(), Length(1, 512), Email()]
    )
    contact_phone_number = StringField(
        'Phone Number',
        validators=[InputRequired(), Length(1, 64)]
    )
    submit = SubmitField('Submit')
