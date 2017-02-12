from .. import db
from ..models import Rating


def normalize_string(s):
    """Return a normalized string for use by the template engine

    Different sources of data (i.e. the given resource.md files, the jekyll
    templates, etc.) expect and use different ways of encoding the names of
    various components of the resource object. This function just normalizes
    resource fields of the form "I Have Capital Letters and Spaces" to the form
    "i_have_capital_letters_and_spaces" so that the jinja template can properly
    render anything thrown at it.
    """
    return s.lower().replace(' ', '_')


class OptionAssociation(db.Model):
    """
    Association between a resource and a descriptor with an index for the
    value of the option. Can have multiple OptionAssociation between an
    option descriptor and resource
    """
    __tablename__ = 'option_associations'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer,
                            db.ForeignKey('resources.id', ondelete='CASCADE'))
    descriptor_id = db.Column(
        db.Integer, db.ForeignKey('descriptors.id', ondelete='CASCADE'))
    option = db.Column(db.Integer)
    resource = db.relationship(
        'ResourceBase', back_populates='option_descriptors')
    descriptor = db.relationship(
        'Descriptor', back_populates='option_resources')

    def __repr__(self):
        return '%s: %s' % (self.descriptor.name,
                           self.descriptor.values[self.option])


class TextAssociation(db.Model):
    """
    Association between a resource and a descriptor with a text field for the
    value of the descriptor. Currently only support one text association between
    a resource and descriptor.
    """
    __tablename__ = 'text_associations'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer,
                            db.ForeignKey('resources.id', ondelete='CASCADE'))
    descriptor_id = db.Column(
        db.Integer, db.ForeignKey('descriptors.id', ondelete='CASCADE'))
    text = db.Column(db.Text)
    resource = db.relationship(
        'ResourceBase', back_populates='text_descriptors')
    descriptor = db.relationship('Descriptor', back_populates='text_resources')

    def __repr__(self):
        return '%s: %s' % (self.descriptor.name, self.text)


class Descriptor(db.Model):
    """
    Schema for descriptors that contain the name and values for an
    attribute of a resource.
    """
    __tablename__ = 'descriptors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    values = db.Column(
        db.PickleType)  # should only have value for option descriptor
    is_searchable = db.Column(db.Boolean)
    text_resources = db.relationship(
        'TextAssociation',
        back_populates='descriptor',
        cascade='all, delete-orphan')
    option_resources = db.relationship(
        'OptionAssociation',
        back_populates='descriptor',
        cascade='all, delete-orphan')

    def __repr__(self):
        return '<Descriptor \'%s\'>' % self.name

    @property
    def is_text_descriptor(self):
        return len(self.values) == 0

    @property
    def is_option_descriptor(self):
        return len(self.values) > 0

    def value_string(self):
        if not self.values:
            return ''
        l = list(self.values)
        l.sort()
        return ', '.join(map(str, l))


class RequiredOptionDescriptor(db.Model):
    """ Option descriptor designated as a required option descriptor meaning
    that all resources need to have an option association for this descriptor.
    Restricted to one.
    """
    __tablename__ = 'required_option_descriptor'
    id = db.Column(db.Integer, primary_key=True)
    descriptor_id = db.Column(db.Integer)
    # -1 if none

    @staticmethod
    def init_required_option_descriptor():
        required_option_descriptor = RequiredOptionDescriptor(descriptor_id=-1)
        db.session.add(required_option_descriptor)
        db.session.commit()


class ResourceBase(db.Model):
    """
    Schema for base class that contains items common to approved resources and
    resource suggestions.
    """
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), index=True)
    address = db.Column(db.String(500))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    text_descriptors = db.relationship(
        'TextAssociation',
        back_populates='resource',
        cascade='all, delete-orphan')
    option_descriptors = db.relationship(
        'OptionAssociation',
        back_populates='resource',
        cascade='all, delete-orphan')
    type = db.Column(db.String(20))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'resource_base'
    }

    def __repr__(self):
        return '<ResourceBase \'%s\'>' % self.name


class Resource(ResourceBase):
    """
    Schema for approved resources.
    """
    suggestions = db.relationship(
        'ResourceSuggestion',
        backref='resource',
        uselist=True,
        remote_side='ResourceSuggestion.id')

    __mapper_args__ = {'polymorphic_identity': 'resource'}

    def __repr__(self):
        return '<Resource \'%s\'>' % self.name

    @staticmethod
    def generate_fake(count=20, center_lat=39.951021, center_long=-75.197243):
        """Generate a number of fake resources for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import randint
        from faker import Faker
        from geopy.geocoders import Nominatim

        geolocater = Nominatim()
        fake = Faker()

        num_options = 5
        options = []

        for i in range(num_options):
            options.append(
                Descriptor(
                    name=fake.word(),
                    values=['True', 'False'],
                    is_searchable=fake.boolean()))

        for i in range(count):

            # Generates random coordinates around Philadelphia.
            latitude = str(fake.geo_coordinate(center=center_lat, radius=0.01))
            longitude = str(
                fake.geo_coordinate(center=center_long, radius=0.01))

            location = geolocater.reverse(latitude + ', ' + longitude)

            # Create one or two resources with that location.
            for i in range(randint(1, 2)):
                resource = Resource(
                    name=fake.name(),
                    address=location.address,
                    latitude=latitude,
                    longitude=longitude)

                oa = OptionAssociation(option=randint(0, 1))
                oa.descriptor = options[randint(0, num_options - 1)]
                resource.option_descriptors.append(oa)

                ta = TextAssociation(text=fake.sentence(nb_words=10))
                ta.descriptor = Descriptor(
                    name=fake.word(), values=[], is_searchable=fake.boolean())
                resource.text_descriptors.append(ta)

                db.session.add(resource)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()

    @staticmethod
    def add_seattle_data():
        from sqlalchemy.exc import IntegrityError
        import os
        import yaml

        resources = os.listdir("_seattle")

        description_descriptor = Descriptor(
            name='description', values=[], is_searchable=True)
        website_descriptor = Descriptor(
            name='website', values=[], is_searchable=True)
        populations_served_descriptor = Descriptor(
            name='populations served', values=[], is_searchable=True)
        hours_descriptor = Descriptor(
            name='hours', values=[], is_searchable=True)
        phone_numbers_descriptor = Descriptor(
            name='phone numbers', values=[], is_searchable=True)
        email_descriptor = Descriptor(
            name='email', values=[], is_searchable=True)
        mailing_address_descriptor = Descriptor(
            name='mailing address', values=[], is_searchable=True)
        contact_form_descriptor = Descriptor(
            name='contact form', values=[], is_searchable=True)
        non_english_services_descriptor = Descriptor(
            name='non english services', values=[], is_searchable=True)
        additional_information_descriptor = Descriptor(
            name='additional information', values=[], is_searchable=True)
        report_count_descriptor = Descriptor(
            name='report_count', values=[], is_searchable=True)

        categories_descriptor = Descriptor(
            name='categories',
            values=[
                'Medical Clinics', 'Women\'s Health', 'Sexual Health',
                'Trans Health', 'Dental Care', 'Legal Aid', 'Documentation',
                'Housing', 'Food', 'Hygiene', 'Computers & Internet',
                'Employment', 'English Classes', 'Libraries',
                'Community Centers', 'LGBT Centers', 'Cultural Centers',
                'Support Groups', 'Private Counseling', 'Psychiatry', 'Mail',
                'Sport & Entertainment'
            ],
            is_searchable=True)

        supercategories_descriptor = Descriptor(
            name='supercategories',
            values=[
                'Medical', 'Legal', 'Education', 'Community', 'Mental Health'
            ],
            is_searchable=True)

        features_descriptor = Descriptor(
            name='features',
            values=[
                'Has A Confidentiality Policy', 'Is Free',
                'Has Translation Services'
            ],
            is_searchable=True)

        city_descriptor = Descriptor(
            name='city',
            values=['Seattle, Washington', 'Philadelphia, Pennsylvania'],
            is_searchable=True)

        requirements_descriptor = Descriptor(
            name='requirements',
            values=[
                'Photo ID', 'Proof of Age', 'Proof of Residence',
                'Proof of Income', 'Medical Insurance', 'A Referral'
            ],
            is_searchable=True)

        script_dir = os.path.dirname("__file__")

        for obj in resources:

            if obj.startswith("."):
                continue

            rel_path = "_seattle/" + obj
            abs_file_path = os.path.join(script_dir, rel_path)
            with open(abs_file_path, 'r') as f:
                doc = yaml.load(f)

            address = doc['address']
            resource = Resource(
                name=doc['name'],
                address=address,
                latitude=doc['lat'],
                longitude=doc['long'])

            description_association = TextAssociation(
                text=doc['description'], descriptor=description_descriptor)
            resource.text_descriptors.append(description_association)

            website_association = TextAssociation(
                text=doc['website'], descriptor=website_descriptor)
            resource.text_descriptors.append(website_association)

            populations_served_association = TextAssociation(
                text=doc['populations_served'],
                descriptor=populations_served_descriptor)
            resource.text_descriptors.append(populations_served_association)

            hours_association = TextAssociation(
                text=doc['hours'], descriptor=hours_descriptor)
            resource.text_descriptors.append(hours_association)

            email_association = TextAssociation(
                text=doc['email'], descriptor=email_descriptor)
            resource.text_descriptors.append(email_association)

            mailing_address_association = TextAssociation(
                text=doc['mailing_address'],
                descriptor=mailing_address_descriptor)
            resource.text_descriptors.append(mailing_address_association)

            contact_form_association = TextAssociation(
                text=doc['contact_form'], descriptor=contact_form_descriptor)
            resource.text_descriptors.append(contact_form_association)

            additional_information_association = TextAssociation(
                text=doc['additional_information'],
                descriptor=additional_information_descriptor)
            resource.text_descriptors.append(
                additional_information_association)

            report_count_association = TextAssociation(
                text=0,
                descriptor=report_count_descriptor)
            resource.text_descriptors.append(
                report_count_association)

            if doc['phone_numbers']:
                phone_numbers = doc['phone_numbers']
                phone_numbers_association = TextAssociation(
                    text=', '.join(phone_numbers),
                    descriptor=phone_numbers_descriptor)
                resource.text_descriptors.append(phone_numbers_association)

            if doc['non_english_services']:
                non_english_services = doc['non_english_services']
                non_english_services_association = TextAssociation(
                    text=', '.join(non_english_services),
                    descriptor=non_english_services_descriptor)
                resource.text_descriptors.append(
                    non_english_services_association)

            categories = doc['categories']
            supercategories = doc['supercategories']
            if 'features' in doc:
                features = doc['features']

            if 'city' in doc:
                city = doc['city']

            if categories:
                for category in categories:
                    category_association = OptionAssociation(
                        descriptor=categories_descriptor,
                        option=categories_descriptor.values.index(category))
                    resource.option_descriptors.append(category_association)

            if supercategories:
                for supercategory in supercategories:
                    supercategory_association = OptionAssociation(
                        descriptor=supercategories_descriptor,
                        option=supercategories_descriptor.values.index(
                            supercategory))
                    resource.option_descriptors.append(
                        supercategory_association)

            if features:
                for feature in features:
                    feature_association = OptionAssociation(
                        descriptor=features_descriptor,
                        option=features_descriptor.values.index(feature))
                    resource.option_descriptors.append(feature_association)

            if city:
                city_association = OptionAssociation(
                    descriptor=city_descriptor,
                    option=city_descriptor.values.index(city))
                resource.option_descriptors.append(city_association)

            if 'requirements' in doc:
                requirements = doc['requirements']
                for requirement in requirements:
                    requirements_association = OptionAssociation(
                        descriptor=requirements_descriptor,
                        option=requirements_descriptor.values.index(requirement))
                    resource.option_descriptors.append(requirements_association)

            db.session.add(resource)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def get_resources_as_dicts(resources):
        # get required option descriptor
        req_opt_desc = RequiredOptionDescriptor.query.all()[0]
        req_opt_desc = Descriptor.query.filter_by(
            id=req_opt_desc.descriptor_id).first()

        resources_as_dicts = []
        for resource in resources:
            res = resource.__dict__

            # set required option descriptor
            req = []
            if req_opt_desc is not None:
                associations = OptionAssociation.query.filter_by(
                    resource_id=resource.id,
                    descriptor_id=req_opt_desc.id).all()
                req = [a.descriptor.values[a.option] for a in associations]
            res['requiredOpts'] = req

            # set ratings
            res['avg_rating'] = resource.get_avg_ratings()

            # .__dict__ returns the SQLAlchemy object as a dict, but it
            # also adds a field '_sa_instance_state' that we don't need,
            # so we delete it.
            if '_sa_instance_state' in res:
                del res['_sa_instance_state']
            resources_as_dicts.append(res)
        return resources_as_dicts

    @staticmethod
    def get_resources_as_full_dicts(resources):
        # maps array of resources to array of useful dictionaries containing
        # all of the information/associations for that resources
        resources_as_dicts = []

        for resource in resources:
            resource_as_dict = resource.__dict__
            resource_as_dict['long'] = resource_as_dict['longitude']
            resource_as_dict['lat'] = resource_as_dict['latitude']

            for td in resource.text_descriptors:
                key = normalize_string(td.descriptor.name)
                value = td.text
                resource_as_dict[key] = value
            for od in resource.option_descriptors:
                key = normalize_string(od.descriptor.name)
                if od.option == '':
                    continue
                value = od.descriptor.values[od.option]
                if key not in resource_as_dict:
                    resource_as_dict[key] = [value]
                else:
                    resource_as_dict[key].append(value)

            if '_sa_instance_state' in resource_as_dict:
                del resource_as_dict['_sa_instance_state']
            if 'text_descriptors' in resource_as_dict:
                del resource_as_dict['text_descriptors']
            if 'option_descriptors' in resource_as_dict:
                del resource_as_dict['option_descriptors']
            resources_as_dicts.append(resource_as_dict)

        return resources_as_dicts

    @staticmethod
    def print_resources():
        resources = Resource.query.all()
        for resource in resources:
            print resource
            print resource.address
            print '(%s , %s)' % (resource.latitude, resource.longitude)
            print resource.text_descriptors
            print resource.option_descriptors

    @staticmethod
    def get_resources_in_city(city):
        city_descriptor = Descriptor.query.filter_by(name='city').first()

        if city not in city_descriptor.values:
            return []

        list_of_cities = city_descriptor.values
        lowercase_cities = [x.lower() for x in list_of_cities]
        city_option = lowercase_cities.index(city.lower())

        opt_resources = OptionAssociation.query.filter_by(
            descriptor=city_descriptor).filter_by(option=city_option)
        resources = []
        for opt_resource in opt_resources:
            if opt_resource.resource.type == 'resource':
                resources.append(opt_resource.resource)

        return resources

    @staticmethod
    def get_list_of_cities():
        city_descriptor = Descriptor.query.filter_by(name='city').first()
        return city_descriptor.values

    def get_avg_ratings(self):
        ratings = Rating.query.filter_by(resource_id=self.id).all()
        if not ratings:
            return 0.0
        total_sum = float(sum(r.rating for r in ratings))
        return '%.1f' % (total_sum / len(ratings))

    def get_all_ratings(self):
        ratings = Rating.query.filter_by(resource_id=self.id).all()
        ratings.sort(key=lambda r: r.submission_time, reverse=True)
        return ratings
