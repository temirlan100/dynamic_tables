import pytest
from django.db import connection
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from dynamicTables.app.models import TableMetadata


class TestTableRowsView:
    @pytest.fixture(autouse=True)
    def setup_method(self, db):
        self.client = APIClient()
        self.url = lambda pk: reverse('get_table_rows', kwargs={'pk': pk})

        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE test_table (
                    id serial PRIMARY KEY,
                    field1 varchar(100),
                    field2 integer
                )
            """)
            cursor.execute("""
                INSERT INTO test_table (field1, field2)
                VALUES ('test_string', 1)
            """)

    @pytest.mark.django_db
    def test_get_table_rows_success(self):
        table_metadata = TableMetadata.objects.create(
            table_name='test_table',
            fields=[{'name': 'field1', 'type': 'string'}, {'name': 'field2', 'type': 'number'}]
        )
        response = self.client.get(self.url(table_metadata.id))
        assert response.status_code == HTTP_200_OK
        assert response.json() == [{'name': 'field1', 'type': 'string'}, {'name': 'field2', 'type': 'number'}]

    @pytest.mark.django_db
    def test_get_table_rows_not_found(self):
        response = self.client.get(self.url(1000))
        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.json()['detail'] == 'Table not found.'
