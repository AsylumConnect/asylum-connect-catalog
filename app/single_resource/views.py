from flask import abort, flash, redirect, render_template, request, url_for
from flask.ext.login import login_required
from sqlalchemy.exc import IntegrityError
from wtforms.fields import SelectMultipleField, TextAreaField

from . import single_resource
from .. import db
from ..models import (Descriptor, OptionAssociation, RequiredOptionDescriptor,
                      Resource, ResourceSuggestion, TextAssociation)
from ..suggestion.forms import ResourceForm
from ..suggestion.views import save_associations
from .forms import SingleResourceForm


@single_resource.route('/')
@login_required
def index():
    """View resources in a list."""
    resources = Resource.query.all()
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    req_opt_desc = Descriptor.query.filter_by(
        id=req_opt_desc.descriptor_id).first()
    req_options = {}
    if req_opt_desc is not None:
        for val in req_opt_desc.values:
            req_options[val] = False
    return render_template(
        'single_resource/index.html',
        resources=resources,
        req_options=req_options)


@single_resource.route('/search')
@login_required
def search_resources():
    name = request.args.get('name')
    if name is None:
        name = ""
    req_options = request.args.getlist('reqoption')
    if req_options is None:
        req_options = []
    resource_pool = Resource.query.filter(Resource.name.contains(name)).all()
    req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    req_opt_desc = Descriptor.query.filter_by(
        id=req_opt_desc.descriptor_id).first()
    resources = list(resource_pool)
    if req_opt_desc is not None and len(req_options) > 0:
        resources = []
        int_req_options = []
        for o in req_options:
            int_req_options.append(req_opt_desc.values.index(str(o)))
        for resource in resource_pool:
            associations = OptionAssociation.query.filter_by(
                resource_id=resource.id, descriptor_id=req_opt_desc.id)
            for a in associations:
                if a.option in int_req_options:
                    resources.append(resource)
                    break
    query_req_options = {}
    if req_opt_desc is not None:
        for val in req_opt_desc.values:
            query_req_options[val] = val in req_options
    return render_template(
        'single_resource/index.html',
        resources=resources,
        query_name=name,
        req_options=query_req_options)


@single_resource.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Add a resource."""
    descriptors = Descriptor.query.all()
    # req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    for descriptor in descriptors:
        if descriptor.is_option_descriptor:  # Fields for option descriptors.
            if descriptor.name != 'supercategories':
                choices = [(str(i), v)
                           for i, v in enumerate(descriptor.values)]
                setattr(
                    SingleResourceForm,
                    descriptor.name,
                    SelectMultipleField(choices=choices))
            else:
                pass
        else:  # Fields for text descriptors
            setattr(SingleResourceForm, descriptor.name, TextAreaField())
    form = SingleResourceForm()
    if form.validate_on_submit():
        new_resource = Resource(
            name=form.name.data,
            address=form.address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data)
        db.session.add(new_resource)
        save_associations(
            resource=new_resource,
            form=form,
            descriptors=descriptors,
            resource_existed=False)
        try:
            db.session.commit()
            flash('Resource added', 'form-success')
            return redirect(url_for('single_resource.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')
    return render_template('single_resource/create.html', form=form)


@single_resource.route('/create/<int:suggestion_id>', methods=['GET', 'POST'])
@login_required
def create_from_suggestion(suggestion_id):
    """Add a resource from suggestion."""
    suggestion = ResourceSuggestion.query.get(suggestion_id)
    if suggestion is None:
        abort(404)

    suggestion_field_names = Resource.__table__.columns.keys()
    descriptors = Descriptor.query.all()
    # req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    for descriptor in descriptors:
        if descriptor.is_option_descriptor:  # Fields for option descriptors.
            if descriptor.name != 'supercategories':
                choices = [(str(i), v)
                           for i, v in enumerate(descriptor.values)]
                default = None
                option_associations = OptionAssociation.query.filter_by(
                    resource_id=suggestion_id, descriptor_id=descriptor.id)
                if option_associations is not None:
                    default = [assoc.option for assoc in option_associations]
                setattr(SingleResourceForm, descriptor.name,
                        SelectMultipleField(choices=choices, default=default))
            else:
                pass
        else:  # Fields for text descriptors
            default = None
            text_association = TextAssociation.query.filter_by(
                resource_id=suggestion_id, descriptor_id=descriptor.id).first()
            if text_association is not None:
                default = text_association.text
            setattr(
                SingleResourceForm,
                descriptor.name,
                TextAreaField(default=default))

    form = SingleResourceForm()
    if form.validate_on_submit():
        new_resource = Resource(
            name=form.name.data,
            address=form.address.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data)
        # Field id is not needed for the form, hence omitted with [1:].
        for field_name in suggestion_field_names[1:]:
            if field_name in form:
                setattr(new_resource, field_name, form[field_name].data)
        save_associations(
            resource=new_resource,
            form=form,
            descriptors=descriptors,
            resource_existed=False)
        db.session.add(new_resource)
        try:
            db.session.commit()
            flash('Resource added', 'form-success')
            db.session.delete(suggestion)
            try:
                db.session.commit()
                flash('Suggestion successfully deleted.', 'success')
            except:
                db.session.rollback()
                flash('Database error occurred. Please try again.', 'error')
            return redirect(url_for('single_resource.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')
    for field_name in suggestion_field_names:
        if field_name in form:
            form[field_name].data = suggestion.__dict__[field_name]

    return render_template('single_resource/create.html', form=form)


@single_resource.route('/<int:resource_id>', methods=['GET', 'POST'])
@login_required
def edit(resource_id):
    """Edit a resource."""
    resource = Resource.query.get(resource_id)
    if resource is None:
        abort(404)
    resource_field_names = Resource.__table__.columns.keys()
    descriptors = Descriptor.query.all()
    # req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    for descriptor in descriptors:
        if descriptor.values:  # Fields for option descriptors.
            choices = [(str(i), v) for i, v in enumerate(descriptor.values)]
            default = None
            option_associations = OptionAssociation.query.filter_by(
                resource_id=resource_id, descriptor_id=descriptor.id)
            if option_associations is not None:
                default = [assoc.option for assoc in option_associations]
            setattr(SingleResourceForm, descriptor.name,
                    SelectMultipleField(choices=choices, default=default))
        else:  # Fields for text descriptors.
            default = None
            text_association = TextAssociation.query.filter_by(
                resource_id=resource_id, descriptor_id=descriptor.id).first()
            if text_association is not None:
                default = text_association.text
            setattr(
                SingleResourceForm,
                descriptor.name,
                TextAreaField(default=default))
    form = SingleResourceForm()
    if form.validate_on_submit():
        # Field id is not needed for the form, hence omitted with [1:].
        for field_name in resource_field_names[1:]:
            # Avoid KeyError from polymorphic, contact variables.
            if field_name in form:
                setattr(resource, field_name, form[field_name].data)
        save_associations(
            resource=resource,
            form=form,
            descriptors=descriptors,
            resource_existed=True)
        try:
            db.session.commit()
            flash('Resource updated', 'form-success')
            return redirect(url_for('single_resource.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')
    # Field id is not needed for the form, hence omitted with [1:].
    for field_name in resource_field_names[1:]:
        if field_name in form:
            form[field_name].data = resource.__dict__[field_name]
    return render_template(
        'single_resource/edit.html', form=form, resource_id=resource_id)


@single_resource.route('/edit/<int:suggestion_id>', methods=['GET', 'POST'])
@login_required
def edit_from_suggestion(suggestion_id):
    """Edit a resource from suggestion."""
    suggestion = ResourceSuggestion.query.get(suggestion_id)
    if suggestion is None:
        abort(404)
    resource = Resource.query.get(suggestion.resource_id)
    if resource is None:
        abort(404)

    resource_field_names = Resource.__table__.columns.keys()
    suggestion_field_names = ResourceSuggestion.__table__.columns.keys()
    descriptors = Descriptor.query.all()
    # req_opt_desc = RequiredOptionDescriptor.query.all()[0]
    for descriptor in descriptors:
        if descriptor.is_option_descriptor:  # Fields for option descriptors.
            if descriptor.name != 'supercategories':
                choices = [(str(i), v)
                           for i, v in enumerate(descriptor.values)]

                default_resource = None
                option_associations_resource = OptionAssociation.query.\
                    filter_by(resource_id=resource.id,
                              descriptor_id=descriptor.id)
                if option_associations_resource is not None:
                    default_resource = [
                        assoc.option for assoc in option_associations_resource
                    ]
                setattr(ResourceForm, descriptor.name,
                        SelectMultipleField(
                            choices=choices, default=default_resource))

                default_suggestion = None
                option_associations_suggestion = OptionAssociation.query.\
                    filter_by(resource_id=suggestion_id,
                              descriptor_id=descriptor.id)
                if option_associations_suggestion is not None:
                    default_suggestion = [
                        assoc.option
                        for assoc in option_associations_suggestion
                    ]
                setattr(SingleResourceForm, descriptor.name,
                        SelectMultipleField(
                            choices=choices, default=default_suggestion))
            else:
                pass
        else:  # Fields for text descriptors
            default_resource = None
            text_association_resource = TextAssociation.query.filter_by(
                resource_id=resource.id, descriptor_id=descriptor.id).first()
            if text_association_resource is not None:
                default_resource = text_association_resource.text
            setattr(
                ResourceForm,
                descriptor.name,
                TextAreaField(default=default_resource))

            default_suggestion = None
            text_association_suggestion = TextAssociation.query.filter_by(
                resource_id=suggestion_id, descriptor_id=descriptor.id).first()
            if text_association_suggestion is not None:
                default_suggestion = text_association_suggestion.text
            setattr(
                SingleResourceForm,
                descriptor.name,
                TextAreaField(default=default_suggestion))

    form_resource = ResourceForm()
    form_suggestion = SingleResourceForm()
    if form_suggestion.validate_on_submit():
        # replace reosurce's fields
        resource.name = form_suggestion.name.data
        resource.address = form_suggestion.address.data
        resource.latitude = form_suggestion.latitude.data
        resource.longitude = form_suggestion.longitude.data
        # Field id is not needed for the form, hence omitted with [1:].
        for field_name in suggestion_field_names[1:]:
            if field_name in form_suggestion:
                setattr(resource, field_name, form_suggestion[field_name].data)
        save_associations(
            resource=resource,
            form=form_suggestion,
            descriptors=descriptors,
            resource_existed=True)
        db.session.add(resource)
        try:
            db.session.commit()
            flash('Resource added', 'form-success')
            db.session.delete(suggestion)
            try:
                db.session.commit()
                flash('Suggestion successfully deleted.', 'success')
            except:
                db.session.rollback()
                flash('Database error occurred. Please try again.', 'error')
            return redirect(url_for('single_resource.index'))
        except IntegrityError:
            db.session.rollback()
            flash('Error: failed to save resource. Please try again.',
                  'form-error')

    for field_name in resource_field_names:
        if field_name in form_resource:
            form_resource[field_name].data = resource.__dict__[field_name]

    for field_name in suggestion_field_names:
        if field_name in form_suggestion:
            form_suggestion[field_name].data = suggestion.__dict__[field_name]

    return render_template(
        'single_resource/edit_from_suggestion.html',
        form_resource=form_resource,
        form=form_suggestion)


category_to_supercategory = {
    "Medical Clinics": "Medical",
    "Women's Health": "Medical",
    "Sexual Health": "Medical",
    "Trans Health": "Medical",
    "Dental Care": "Medical",
    "Legal Aid": "Legal",
    "Documentation": "Legal",
    "English Classes": "Education",
    "Libraries": "Education",
    "Community Centers": "Community",
    "LGBT Centers": "Community",
    "Cultural Centers": "Community",
    "Support Groups": "Mental Health",
    "Private Counseling": "Mental Health",
    "Psychiatry": "Mental Health"
}


@single_resource.route('/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete(resource_id):
    """Delete a resource."""
    resource = Resource.query.get(resource_id)
    db.session.delete(resource)
    try:
        db.session.commit()
        flash('Resource deleted', 'form-success')
        return redirect(url_for('single_resource.index'))
    except IntegrityError:
        db.session.rollback()
        flash('Error: failed to delete resource. Please try again.',
              'form-error')
