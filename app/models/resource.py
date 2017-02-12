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
    value of the descriptor. Currently only support one text association
    between a resource and descriptor.
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

        text_descriptors_names =\
            ['description', 'website', 'populations served', 'hours',
             'phone numbers', 'email', 'mailing address', 'contact form',
             'non english services', 'additional information', 'report count']

        list_text_descriptor_names = ['phone numbers', 'non english services']

        text_descriptors = {}
        for text_descriptors_name in text_descriptors_names:
            text_descriptors[text_descriptors_name] = Descriptor(
                name=text_descriptors_name, values=[], is_searchable=True
            )

        option_descriptor_values = {}
        option_descriptor_values['categories'] =\
            ['Medical Clinics', 'Women\'s Health', 'Sexual Health',
             'Trans Health', 'Dental Care', 'Legal Aid', 'Documentation',
             'Housing', 'Food', 'Hygiene', 'Computers and Internet',
             'Employment', 'English Classes', 'Libraries',
             'Community Centers', 'LGBT Centers', 'Cultural Centers',
             'Support Groups', 'Private Counseling', 'Psychiatry', 'Mail',
             'Sport and Entertainment']

        option_descriptor_values['supercategories'] =\
            ['Medical', 'Legal', 'Education', 'Community', 'Mental Health']

        option_descriptor_values['features'] =\
            ['Has A Confidentiality Policy', 'Is Free',
             'Has Translation Services']

        option_descriptor_values['requirements'] = \
            ['Photo ID', 'Proof of Age', 'Proof of Residence',
             'Proof of Income', 'Medical Insurance', 'A Referral']

        option_descriptor_values['city'] =\
            ['Seattle, Washington', 'Philadelphia, Pennsylvania']

        option_descriptor_names = \
            ['city', 'categories', 'supercategories', 'features',
             'requirements']

        singleton_option_descriptor_names = ['city']

        option_descriptors = {}
        for option_descriptor_name in option_descriptor_names:
            option_descriptors[option_descriptor_name] = Descriptor(
                name=option_descriptor_name,
                values=option_descriptor_values[option_descriptor_name],
                is_searchable=True
            )

        script_dir = os.path.dirname("__file__")

        for obj in resources:

            if obj.startswith("."):
                continue

            rel_path = "_seattle/" + obj
            abs_file_path = os.path.join(script_dir, rel_path)
            with open(abs_file_path, 'r') as f:
                doc = yaml.load(f)

                resource = Resource(
                    name=doc['name'],
                    address=doc['address'],
                    latitude=doc['lat'],
                    longitude=doc['long'])

                for option_descriptor_name in option_descriptor_names:
                    print option_descriptor_name
                    if option_descriptor_name in doc and \
                            doc[option_descriptor_name]:
                        print doc[option_descriptor_name]
                        if option_descriptor_name in \
                                singleton_option_descriptor_names:
                            this_descriptor = \
                                option_descriptors[option_descriptor_name]
                            print this_descriptor.values
                            resource.option_descriptors.append(
                                OptionAssociation(
                                    descriptor=this_descriptor,
                                    option=this_descriptor.values.index(
                                        doc[option_descriptor_name])
                                ))
                        else:
                            this_descriptor = \
                                option_descriptors[option_descriptor_name]
                            print this_descriptor
                            for item in doc[option_descriptor_name]:
                                resource.option_descriptors.append(
                                    OptionAssociation(
                                        descriptor=this_descriptor,
                                        option=this_descriptor.values.index(
                                            item)
                                    )
                                )

                for text_descriptors_name in text_descriptors_names:
                    print text_descriptors_name
                    key_name = '_'.join(text_descriptors_name.split(' '))
                    if key_name in doc and doc[key_name] and key_name !=\
                            "report_count":
                        this_text = doc[key_name]
                        print doc[key_name]
                        if text_descriptors_name in list_text_descriptor_names:
                            this_text = ', '.join(doc[key_name])
                        resource.text_descriptors.append(TextAssociation(
                            text=this_text,
                            descriptor=text_descriptors[text_descriptors_name]
                        ))

                resource.text_descriptors.append(TextAssociation(
                    text=0, descriptor=text_descriptors["report count"]))

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
