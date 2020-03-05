import functools
import json
import os

from peewee import CharField, Model, TextField
from playhouse.db_url import connect
from playhouse.postgres_ext import JSONField, TSVectorField


db = connect(os.environ["DATABASE_URL"])


# The schema generator uses Python sets for some data structures. This will
# convert them to a list when we serialize to JSON when storing the probe
# representation to the database.
class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class Probes(Model):
    product = CharField()
    name = CharField()
    type = CharField()
    description = TextField()
    definition = JSONField(functools.partial(json.dumps, cls=SetEncoder))
    index = TSVectorField()

    class Meta:
        database = db
        indexes = ((("product", "name"), True),)


db.connect()
# This is a no-op if the table already exists.
db.create_tables([Probes])
