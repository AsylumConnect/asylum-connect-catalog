from wtforms.fields import SubmitField

from ..suggestion.forms import ResourceForm


class SingleResourceForm(ResourceForm):
    submit = SubmitField('Save Resource')
