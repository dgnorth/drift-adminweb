"""
    Utilities functions assisting the system tests
"""
import httplib
import datetime
from mock import patch

from drift.core.extensions.schemachecker import validate,\
    generate_validation_error_report
from drift.systesthelper import DriftBaseTestCase, user_payload
from jsonschema import ValidationError


class BaseTestCase(DriftBaseTestCase):

    def get_schema(self, schema_name):
        r = self.get("/schemas/" + schema_name)
        return r.json()

    def validate_schema(self, data, schema_name):
        schema = self.get_schema(schema_name)
        try:
            validate(data, schema)
        except ValidationError as e:
            report = generate_validation_error_report(e, data)
            message = "Json schema validation failed for '%s'\n%s" % (
                schema_name, report)
            self.fail(message)

    def get_resource(self, uri):
        r = self.get(uri)
        return r.json()

    def validate_resource_not_exist(self, uri):
        self.get(uri, expected_status_code=httplib.NOT_FOUND)

