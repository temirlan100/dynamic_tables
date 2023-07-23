import pytest
from django.db import connection
from django.urls import reverse
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from dynamicTables.app.models import TableMetadata


class TestUpdateTableRowView:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.client = APIClient()
        self.url = lambda pk: reverse('update_table_row', kwargs={'pk': pk})
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE test_table (
                    id serial PRIMARY KEY,
                    field1 varchar(100),
                    field2 integer
                )
            """)

    @pytest.mark.django_db
    def test_update_table_row_success(self):
        table_metadata = TableMetadata.objects.create(
            table_name='test_table',
            fields=[{'name': 'field1', 'type': 'string'},
                    {'name': 'field2', 'type': 'number'}]
        )
        data = {
            'fields': [{'name': 'new_field1', 'type': 'string'}, {'name': 'new_field2', 'type': 'number'}]
        }
        response = self.client.post(self.url(table_metadata.id), data, format='json')
        assert response.status_code == HTTP_200_OK
        assert response.json()['detail'] == 'Table updated.'

    @pytest.mark.django_db
    def test_update_table_row_not_found(self):
        data = {
            'fields': [{'name': 'field1', 'type': 'string'}, {'name': 'field2', 'type': 'number'}]
        }
        response = self.client.post(self.url(1000), data, format='json')
        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()['detail'] == 'Table not found.'

    @pytest.mark.django_db
    def test_update_table_row_invalid_data(self):
        table_metadata = TableMetadata.objects.create(
            table_name='test_table',
            fields=[{'name': 'field1', 'type': 'string'},
                    {'name': 'field2', 'type': 'number'}]
        )
        data = {
            'fields': [{'name': 'field1', 'type': 'invalid_type'}]
        }
        response = self.client.post(self.url(table_metadata.id), data, format='json')
        assert response.status_code == HTTP_400_BAD_REQUEST
