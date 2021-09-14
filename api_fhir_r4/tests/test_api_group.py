import json
import os

from django.utils.translation import gettext as _
from api_fhir_r4.utils import DbManagerUtils
from insuree.test_helpers import *
from rest_framework.test import APITestCase
from rest_framework import status
from fhir.resources.group import Group
from api_fhir_r4.tests import GenericFhirAPITestMixin, GroupTestMixin
from api_fhir_r4.configurations import GeneralConfiguration
from core.models import User
from core.services import create_or_update_interactive_user, create_or_update_core_user


class GroupAPITests(GenericFhirAPITestMixin, APITestCase):

    base_url = GeneralConfiguration.get_base_url()+'Group/'
    _test_json_path = "/test/test_group.json"
    _TEST_INSUREE_CHFID = "TestCfhId1"
    _TEST_INSUREE_LAST_NAME = "Test"
    _TEST_INSUREE_OTHER_NAMES = "TestInsuree"
    _TEST_POVERTY_STATUS = True
    _TEST_INSUREE_CHFID_NOT_EXIST = "NotExistedCHF"

    _test_json_path_credentials = "/tests/test/test_login.json"
    _TEST_USER_NAME = "TestUserTest2"
    _TEST_USER_PASSWORD = "TestPasswordTest2"
    _TEST_DATA_USER = {
        "username": _TEST_USER_NAME,
        "last_name": _TEST_USER_NAME,
        "password": _TEST_USER_PASSWORD,
        "other_names": _TEST_USER_NAME,
        "user_types": "INTERACTIVE",
        "language": "en",
        "roles": [1],
    }
    _test_request_data_credentials = None

    def setUp(self):
        super(GroupAPITests, self).setUp()
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        json_representation = open(dir_path + self._test_json_path_credentials).read()
        self._test_request_data_credentials = json.loads(json_representation)
        print('after test')
        print(User.objects.filter(username=self._TEST_USER_NAME).count())
        self.get_or_create_user_api()
        print('before test')
        print(User.objects.filter(username=self._TEST_USER_NAME).count())

    def get_or_create_user_api(self):
        user = DbManagerUtils.get_object_or_none(User, username=self._TEST_USER_NAME)
        if user is None:
            user = self.__create_user_interactive_core()
        return user

    def __create_user_interactive_core(self):
        i_user, i_user_created = create_or_update_interactive_user(
            user_id=None, data=self._TEST_DATA_USER, audit_user_id=999, connected=False)
        create_or_update_core_user(
            user_uuid=None, username=self._TEST_DATA_USER["username"], i_user=i_user)
        return DbManagerUtils.get_object_or_none(User, username=self._TEST_USER_NAME)

    def verify_updated_obj(self, updated_obj):
        self.assertTrue(isinstance(updated_obj, Group))
        poverty_data = None
        for extension in updated_obj.extension:
            if "group-poverty-status" in extension.url:
                poverty_data = extension
        self.assertEqual(self._TEST_POVERTY_STATUS, poverty_data.valueBoolean)

    def update_resource(self, data):
        for extension in data["extension"]:
            if "group-poverty-status" in extension["url"]:
                extension["valueBoolean"] = self._TEST_POVERTY_STATUS

    def create_dependencies(self):
        insuree = create_test_insuree(
            with_family=False,
            custom_props=
            {
                "chf_id": self._TEST_INSUREE_CHFID,
                "last_name": self._TEST_INSUREE_LAST_NAME,
                "other_names": self._TEST_INSUREE_OTHER_NAMES,
            }
        )
        imis_location = GroupTestMixin().create_mocked_location()
        imis_location.save()

    def update_payload_no_extensions(self, data):
        data["extension"] = []
        return data

    def update_payload_no_such_chf_id(self, data):
        for member in data["member"]:
            member["entity"]["identifier"]["value"] = self._TEST_INSUREE_CHFID_NOT_EXIST
        return data

    def update_payload_remove_chf_id_from_it(self, data):
        for member in data["member"]:
            member["entity"]["identifier"].pop("value")
        return data

    def test_post_should_create_correctly(self):
        self.create_dependencies()
        response = self.client.post(
            GeneralConfiguration.get_base_url() + 'login/', data=self._test_request_data_credentials, format='json'
        )
        response_json = response.json()
        token = response_json["token"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = {
            "Content-Type": "application/json",
            'HTTP_AUTHORIZATION': f"Bearer {token}"
        }
        response = self.client.post(self.base_url, data=self._test_request_data, format='json', **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.content)

    def test_post_should_raise_error_no_extensions(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_no_extensions(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _("At least one extension with address is required")
        )

    def test_post_should_raise_error_no_such_chf_id(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_no_such_chf_id(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _('Such insuree %(chf_id)s does not exist') % {'chf_id': self._TEST_INSUREE_CHFID_NOT_EXIST}
        )

    def test_post_should_raise_error_no_chf_id_in_payload(self):
        self.login()
        self.create_dependencies()
        modified_payload = self.update_payload_remove_chf_id_from_it(data=self._test_request_data)
        response = self.client.post(self.base_url, data=modified_payload, format='json')
        response_json = response.json()
        self.assertEqual(
            response_json["issue"][0]["details"]["text"],
            _("Family Group FHIR without code - this field is obligatory")
        )
