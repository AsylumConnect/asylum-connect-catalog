from flask import render_template, request
from . import main
from ..models import Resource
import json


@main.route('/', methods=['GET'])
def index():
    return render_template('main/index.html')


@main.route('/get-resource', methods=['GET'])
def getResource():
    Resource.generate_fake()
    names = Resource.query.with_entities(Resource.name)
    lats = Resource.query.with_entities(Resource.latitude)
    longs = Resource.query.with_entities(Resource.longitude)
    data = []
    counter = 0
    for name in names:
        this_pin = {'Name': name, 'Latitude': lats[counter], 'Longitude':
            longs[counter]}
        counter = counter + 1
        data.append(this_pin)
    return json.dumps(data)


@main.route('/get-info', methods=['POST'])
def getInfo():
    print request.form.data
    return json.dumps({'Address': 'test', 'Description': 'decrption test text'})

