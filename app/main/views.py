import json
from datetime import datetime

from flask import jsonify, redirect, render_template, request, url_for
from flask.ext.login import login_required

from app import csrf

from . import main
from .. import db
from ..models import EditableHTML, Rating, Resource


@main.route('/')
def index():
    return redirect(url_for('.city_view', city_name='seattle'))


@main.route('/catalog/<string:city_name>')
def city_view(city_name):
    city = city_name.title()

    cities = Resource.get_list_of_cities()
    category_icons = [
        'housing', 'food', 'hygiene', 'computers', 'employment', 'mail',
        'recreation'
    ]
    ''' RESOURCE STRUCTURE:
        categories = list of string categories
        features = list of string features
        name = string
        supercategories = list of strings
        address = string
        lat =
        long =
        website = string
    '''

    resources = Resource.get_resources_in_city(city)
    resources_as_dicts = Resource.get_resources_as_full_dicts(resources)

    return render_template(
        'main/index.html',
        city=city,
        cities=cities,
        resources=resources_as_dicts,
        category_icons=category_icons)


@main.route('/get-resources')
def get_resources():
    resources = Resource.query.all()
    resources_as_dicts = Resource.get_resources_as_full_dicts(resources)
    return json.dumps(resources_as_dicts)


@main.route('/search-resources/<query_name>')
def search_resources(query_name):
    resources = Resource.query.filter(Resource.name.contains(query_name))
    resources_as_dicts = Resource.get_resources_as_dicts(resources)
    return json.dumps(resources_as_dicts)


@main.route('/get-associations/<int:resource_id>')
def get_associations(resource_id):
    resource = Resource.query.get(resource_id)
    associations = {}
    if resource is None:
        return json.dumps(associations)
    for td in resource.text_descriptors:
        associations[td.descriptor.name] = td.text
    for od in resource.option_descriptors:
        associations[od.descriptor.name] = od.descriptor.values[od.option]
    return json.dumps(associations)


@main.route('/update-editor-contents', methods=['POST'])
@login_required
def update_editor_contents():
    """Update the contents of an editor."""
    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')
    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data
    db.session.add(editor_contents)
    db.session.commit()
    return 'OK', 200


@csrf.exempt
@main.route('/resource-view', methods=['POST'])
def post_rating():
    if request is not None:
        time = datetime.now()
        star_rating = request.json['rating']
        comment = request.json['review']
        if comment and star_rating:
            rating = Rating(
                submission_time=time, rating=star_rating, review=comment)
            db.session.add(rating)
            db.session.commit()
        elif star_rating:
            rating = Rating(submission_time=time, rating=star_rating)
            db.session.add(rating)
            db.session.commit()
    return jsonify(status='success')


@main.route('/resource-view', methods=['GET'])
def resource():
    return render_template('main/resource.html')
