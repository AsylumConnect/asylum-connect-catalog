from datetime import datetime

import pytz
from flask import abort, flash, redirect, render_template, url_for
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError
from wtforms.fields import FormField, SelectField, StringField, TextAreaField

from forms import ContactInformationForm, ResourceSuggestionForm

from . import suggestion
from .. import db
from ..models import (Descriptor, OptionAssociation, Resource, ResourceBase,
                      ResourceSuggestion, TextAssociation)
from ..single_resource.forms import SingleResourceForm
from ..single_resource.views import save_associations


@suggestion.route('/')
@login_required
def index():
    """View all suggestions in a list."""
    suggestions = ResourceSuggestion.query.all()
    return render_template('suggestion/index.html', suggestions=suggestions)


@suggestion.route('/unread')
@login_required
def unread():
    """Returns the number of unread suggestions."""
    num_unread = ResourceSuggestion.query.filter(
        ResourceSuggestion.read == False  # noqa
    ).count()
    return "%d" % num_unread


@suggestion.route('/toggle-read/<int:sugg_id>')
@login_required
def toggle_read(sugg_id):
    """Toggles the readability of a given suggestion."""
    suggestion = ResourceSuggestion.query.get(sugg_id)
    if suggestion is None:
        abort(404)
    suggestion.read = not suggestion.read
    db.session.add(suggestion)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash('Database error occurred. Please try again.', 'error')
    return redirect(url_for('suggestion.index'))


@suggestion.route('/delete/<int:sugg_id>')
@login_required
def delete(sugg_id):
    """Delete a given suggestion."""
    suggestion = ResourceSuggestion.query.get(sugg_id)
    if suggestion is None:
        abort(404)
    db.session.delete(suggestion)
    try:
        db.session.commit()
        flash('Suggestion successfully deleted.', 'success')
    except:
        db.session.rollback()
        flash('Database error occurred. Please try again.', 'error')
    return redirect(url_for('suggestion.index'))


@suggestion.route('/new', methods=['GET', 'POST'])
def suggest_create():
    """Create a suggestion for a resource."""
    descriptors = Descriptor.query.all()
    for descriptor in descriptors:
        if descriptor.is_option_descriptor:  # Fields for option descriptors.
            choices = [(str(i), v) for i, v in enumerate(descriptor.values)]
            setattr(
                ResourceSuggestionForm,
                descriptor.name,
                SelectField(choices=choices))
        else:  # Fields for text descriptors.
            setattr(ResourceSuggestionForm, descriptor.name, TextAreaField())

    # Add form fields asking for the suggester's name, email, and phone number.
    # Dynamically added here so that form's fields are displayed in the
    # correct order.
    setattr(ResourceSuggestionForm, 'contact_information',
            FormField(ContactInformationForm))

    form = ResourceSuggestionForm()

    if form.validate_on_submit():
        resource_suggestion = ResourceSuggestion(
            name=form.name.data,
            address=form.address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            contact_name=form.contact_information.contact_name.data,
            contact_email=form.contact_information.contact_email.data,
            contact_phone_number=form.contact_information.contact_phone_number.
            data,
            additional_information=form.contact_information.
            additional_information.data,
            submission_time=datetime.now(pytz.timezone('US/Eastern')))
        save_associations(
            resource_suggestion=resource_suggestion,
            form=form,
            descriptors=descriptors)
        db.session.add(resource_suggestion)
        try:
            db.session.commit()
            flash('Thanks for the suggestion!', 'success')
            return redirect(url_for('main.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'error')
    return render_template('suggestion/suggest.html', form=form, name=None)


@suggestion.route('/<int:resource_id>', methods=['GET', 'POST'])
def suggest_edit(resource_id):
    resource = Resource.query.get(resource_id)
    if resource is None:
        abort(404)
    name = resource.name

    resource_field_names = ['name', 'address', 'latitude', 'longitude']
    descriptors = Descriptor.query.all()
    for descriptor in descriptors:
        if descriptor.is_option_descriptor:
            choices = [(str(i), v) for i, v in enumerate(descriptor.values)]
            default = None
            option_association = OptionAssociation.query.filter_by(
                resource_id=resource_id, descriptor_id=descriptor.id).first()
            if option_association is not None:
                default = option_association.option
            setattr(
                ResourceSuggestionForm,
                descriptor.name,
                SelectField(
                    choices=choices, default=default))
        else:  # Fields for text descriptors.
            default = None
            text_association = TextAssociation.query.filter_by(
                resource_id=resource_id, descriptor_id=descriptor.id).first()
            if text_association is not None:
                default = text_association.text
            setattr(
                ResourceSuggestionForm,
                descriptor.name,
                TextAreaField(default=default))

    # Add form fields asking for the suggester's name, email, and phone number.
    # Dynamically added here so that form's fields are displayed in the
    # correct order.
    setattr(ResourceSuggestionForm, 'contact_information',
            FormField(ContactInformationForm))

    form = ResourceSuggestionForm()

    if form.validate_on_submit():
        resource_suggestion = ResourceSuggestion(
            resource_id=resource.id,
            name=form.name.data,
            address=form.address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            contact_name=form.contact_information.contact_name.data,
            contact_email=form.contact_information.contact_email.data,
            contact_phone_number=form.contact_information.contact_phone_number.
            data,
            additional_information=form.contact_information.
            additional_information.data,
            submission_time=datetime.now(pytz.timezone('US/Eastern')))
        # Field id is not needed for the form, hence omitted with [1:].
        for field_name in resource_field_names[1:]:
            setattr(resource_suggestion, field_name, form[field_name].data)
        save_associations(
            resource_suggestion=resource_suggestion,
            form=form,
            descriptors=descriptors)
        db.session.add(resource_suggestion)
        try:
            db.session.commit()
            flash('Thanks for the suggestion!', 'success')
            return redirect(url_for('main.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Database error occurred. Please try again.', 'error')

    for field_name in resource_field_names:
        form[field_name].data = resource.__dict__[field_name]

    return render_template('suggestion/suggest.html', form=form, name=name)


def save_associations(resource_suggestion, form, descriptors):
    """Save associations from the forms received by 'create' and 'edit' route
    handlers to the database."""
    for descriptor in descriptors:
        if descriptor.is_option_descriptor:
            AssociationClass = OptionAssociation
            value = int(form[descriptor.name].data)
            keyword = 'option'
        else:
            AssociationClass = TextAssociation
            value = form[descriptor.name].data
            keyword = 'text'
        arguments = {
            'resource_id': resource_suggestion.id,
            'descriptor_id': descriptor.id,
            keyword: value,
            'resource': resource_suggestion,
            'descriptor': descriptor
        }
        new_association = AssociationClass(**arguments)
        db.session.add(new_association)
