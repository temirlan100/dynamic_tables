import pytest
from django.urls import reverse
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from dynamicTables.app.models import TableMetadata


class TestUpdateTableView:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = APIClient()
        self.url = lambda pk: reverse('update_table', kwargs={'pk': pk})

    @pytest.mark.django_db
    def test_update_table_success(self):
        table_metadata = TableMetadata.objects.create(
            table_name='test_table',
            fields=[
                {'name': 'field1', 'type': 'string'},
                {'name': 'field2', 'type': 'number'}
            ])
        data = {
            'fields': [{'name': 'new_field1', 'type': 'string'}, {'name': 'new_field2', 'type': 'number'}]
        }
        response = self.client.put(self.url(table_metadata.id), data, format='json')
        assert response.status_code == HTTP_200_OK
        assert response.json()['detail'] == 'Table structure replaced.'

    @pytest.mark.django_db
    def test_update_table_not_found(self):
        data = {
            'fields': [{'name': 'field1', 'type': 'string'}, {'name': 'field2', 'type': 'number'}]
        }
        response = self.client.put(self.url(1000), data, format='json')
        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()['detail'] == 'Table not found.'

    @pytest.mark.django_db
    def test_update_table_invalid_data(self):
        table_metadata = TableMetadata.objects.create(
            table_name='test_table',
            fields=[{'name': 'field1', 'type': 'string'},
                    {'name': 'field2', 'type': 'number'}]
        )
        data = {
            'fields': [{'name': 'field1', 'type': 'invalid_type'}]
        }
        response = self.client.put(self.url(table_metadata.id), data, format='json')
        assert response.status_code == HTTP_400_BAD_REQUEST
