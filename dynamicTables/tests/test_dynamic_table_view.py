import pytest
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APIClient


class TestDynamicTableView:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('add_table')

    @pytest.mark.django_db
    def test_create_table_success(self):
        data = {
            'table_name': 'test_table',
            'fields': [{'name': 'field1', 'type': 'string'}, {'name': 'field2', 'type': 'number'}]
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == HTTP_201_CREATED
        assert response.json()['detail'] == 'Table created.'

    @pytest.mark.django_db
    def test_create_table_failed_with_same_table_name(self):
        data = {
            'table_name': 'test_table',
            'fields': [{'name': 'field1', 'type': 'string'}, {'name': 'field2', 'type': 'number'}]
        }
        self.client.post(self.url, data, format='json')
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert response.json()['detail'] == 'Table already exists.'

    @pytest.mark.django_db
    def test_create_table_failed_with_incorrect_fields(self):
        data = {
            'table_name': 'test_table',
            'fields': [{'name': 'field1', 'type': 'integer'}]
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == HTTP_400_BAD_REQUEST
