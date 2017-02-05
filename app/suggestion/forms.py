from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, Length


class ContactInformationForm(Form):
    contact_name = StringField('Contact Name', validators=[Length(0, 512)])
    contact_email = StringField('Contact Email', validators=[Length(0, 512)])
    contact_phone_number = StringField(
        'Contact Phone Number', validators=[Length(0, 64)])
    additional_information = TextAreaField(
        'Additional Information',
        description='Is there anything else about this resource you would '
        'like to share?')


class ResourceSuggestionForm(Form):
    name = StringField('Resource Name', validators=[InputRequired(),
                                                    Length(1, 512)])
    address = StringField(
        'Address', validators=[InputRequired(), Length(1, 512)])
    latitude = HiddenField('Latitude', validators=[InputRequired()])
    longitude = HiddenField('Longitude', validators=[InputRequired()])
    submit = SubmitField('Submit')
