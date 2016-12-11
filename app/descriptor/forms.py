from flask.ext.wtf import Form
from wtforms.fields import (BooleanField, FieldList, SelectField,
                            SelectMultipleField, StringField, SubmitField)
from wtforms.validators import InputRequired, Length


class NewDescriptorForm(Form):
    desc_type = SelectField(
        'Descriptor type',
        choices=[('Text', 'Text'), ('Option', 'Option')],
        validators=[InputRequired()])
    name = StringField('Name', validators=[InputRequired(), Length(1, 64)])
    option_values = FieldList(StringField('Option', [Length(0, 64)]))
    is_searchable = BooleanField('Searchable')
    submit = SubmitField('Add descriptor')


class EditDescriptorNameForm(Form):
    name = StringField('Name', validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('Update name')


class EditDescriptorSearchableForm(Form):
    is_searchable = BooleanField('Searchable')
    submit = SubmitField('Update')


class EditDescriptorOptionValueForm(Form):
    value = StringField(
        'Option Value', validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('Update option value')


class AddDescriptorOptionValueForm(Form):
    value = StringField('', validators=[InputRequired(), Length(1, 64)])
    submit = SubmitField('Add option')


class FixAllResourceOptionValueForm(Form):
    submit = SubmitField('Update resource option values')


class ChangeRequiredOptionDescriptorForm(Form):
    submit = SubmitField('Change')


class RequiredOptionDescriptorMissingForm(Form):
    resources = FieldList(SelectMultipleField(validators=[InputRequired()]))
    submit = SubmitField('Update')
