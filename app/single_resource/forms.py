from wtforms.fields import SubmitField, StringField

from ..suggestion.forms import ResourceForm


class SingleResourceForm(ResourceForm):
    latitude = StringField('Latitude', validators=[])
    longitude = StringField('Longitude', validators=[])
    submit = SubmitField('Save Resource')
