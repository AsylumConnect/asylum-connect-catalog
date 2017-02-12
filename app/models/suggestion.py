from datetime import datetime

import pytz

from .. import db
from ..models.resource import ResourceBase, Resource


class ResourceSuggestion(ResourceBase):
    """
    Schema for resource suggestions, which are either new resources to be added
    or changes to be made to existing resources.
    """
    # resource_id = db.Column(db.Integer, db.ForeignKey(Resource.id))
    resource_id = db.Column(db.Integer,
                            db.ForeignKey('resources.id', ondelete='CASCADE'))
    additional_information = db.Column(db.String(250))
    # 0 stands for read, 1 stands for unread.
    read = db.Column(db.Boolean, default=False)
    submission_time = db.Column(db.DateTime)
    contact_name = db.Column(db.String(500))
    contact_email = db.Column(db.String(500))
    contact_phone_number = db.Column(db.String(64))
    resource_name = db.Column(db.String(500))
    resource_address = db.Column(db.String(500))

    __mapper_args__ = {'polymorphic_identity': 'resource_suggestion'}

    def __repr__(self):
        return '<ResourceSuggestion %s: %s>' % (self.id, self.resource_id)

    @staticmethod
    def generate_fake_inserts(count=20):
        """Generate a number of fake insert suggestions."""
        from sqlalchemy.exc import IntegrityError
        from faker import Faker

        fake = Faker()

        num_words = 10
        for i in range(count):
            s_text = fake.sentence(nb_words=num_words)
            s_read = 1
            s_timestamp = datetime.now(pytz.timezone('US/Eastern'))
            s_contact_name = fake.word()
            s_contact_email = fake.word() + '@' + fake.word() + '.com'
            s_contact_number = '123-456-7890'
            s_insert = ResourceSuggestion(
                additional_information=s_text,
                read=s_read,
                submission_time=s_timestamp,
                contact_name=s_contact_name,
                contact_email=s_contact_email,
                contact_phone_number=s_contact_number)
            db.session.add(s_insert)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def generate_fake_edits(count=20):
        """Generate a number of fake edit suggestions"""
        from sqlalchemy.exc import IntegrityError
        from faker import Faker
        from random import choice

        fake = Faker()

        num_words = 10
        resources = Resource.query.all()
        if len(resources) == 0:
            raise Exception('Resources must exist in order to generate fake '
                            'edits.')
        for i in range(count):
            r = choice(resources)

            s_additional_information = fake.sentence(nb_words=num_words)
            s_read = 0
            s_timestamp = datetime.now(pytz.timezone('US/Eastern'))
            s_contact_name = fake.word()
            s_contact_email = fake.word() + '@' + fake.word() + '.com'
            s_contact_number = '123-456-7890'
            s_edit = ResourceSuggestion(
                resource_id=r.id,
                additional_information=s_additional_information,
                read=s_read,
                submission_time=s_timestamp,
                contact_name=s_contact_name,
                contact_email=s_contact_email,
                contact_phone_number=s_contact_number)
            db.session.add(s_edit)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
