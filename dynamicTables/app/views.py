from django.db import connection
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from dynamicTables.app.models import TableMetadata
from dynamicTables.app.serializers import (
    DynamicTableSerializer,
    UpdateTableSerializer,
    FieldSerializer
)
from dynamicTables.app.utils import get_sql_field_type


class DynamicTableView(APIView):
    """
    The DynamicTableView is a Django REST Framework view that provides an API endpoint for creating a table in the database.
    It inherits from the APIView provided by the Django REST Framework.

    Methods:
        post: Accepts a POST request with a JSON body. The JSON should contain 'table_name' and 'fields' key-value pairs.
                'table_name' is the name of the table to be created.
                'fields' is a list of dictionaries, each containing 'name' and 'type' of the field.
                Creates a table in the database with the provided name and fields.
                If the table already exists, it returns an HTTP 400 Bad Request status.
                If the table is successfully created, it returns an HTTP 201 Created status.
    """

    @swagger_auto_schema(
        request_body=DynamicTableSerializer,
        operation_description="Endpoint for create table in DB"
    )
    def post(self, request):
        """
        Accepts a POST request with a JSON body. The JSON should contain 'table_name' and 'fields' key-value pairs.
        'table_name' is the name of the table to be created.
        'fields' is a list of dictionaries, each containing 'name' and 'type' of the field.

        Parameters:
            request: A Django REST Framework request object.

        Returns:
            If the table already exists, it returns an HTTP 400 Bad Request status with a JSON body containing
            'detail': 'Table already exists.'

            If the table is successfully created, it returns an HTTP 201 Created status with a JSON body containing
            'detail': 'Table created.'

            If there is any validation error in the input, it returns an HTTP 400 Bad Request status with a JSON body
            containing the validation errors.
        """
        serializer = DynamicTableSerializer(data=request.data)
        if serializer.is_valid():
            table_name = serializer.validated_data['table_name']
            fields = serializer.validated_data['fields']

            with connection.cursor() as cursor:
                tables = connection.introspection.table_names(cursor)
                if table_name in tables:
                    return Response({'detail': 'Table already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            table_fields = ', '.join(
                [f"{field['name']} {get_sql_field_type(field['type'])}" for field in fields]
            )

            sql = f"CREATE TABLE {table_name} (id serial PRIMARY KEY, {table_fields});"

            with connection.cursor() as cursor:
                cursor.execute(sql)

            TableMetadata.save_entity(table_name=table_name, fields=fields)

            return Response({'detail': 'Table created.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateTableView(APIView):
    """
    The UpdateTableView is a Django REST Framework view that provides an API endpoint for replacing the rows in a table
    in the database. It inherits from the APIView provided by the Django REST Framework.

    Methods:
        put: Accepts a PUT request with a JSON body. The JSON should contain 'fields' key-value pairs.
             'fields' is a list of dictionaries, each containing 'name' and 'type' of the field.
             Replaces all existing rows in the specified table with new rows as per the fields data.
             If the table does not exist, it returns an HTTP 404 Not Found status.
             If the table is successfully updated, it returns an HTTP 200 OK status.
    """

    @swagger_auto_schema(
        request_body=UpdateTableSerializer,
        operation_description="Endpoint for replace rows in table in DB"
    )
    def put(self, request, pk):
        """
        Accepts a PUT request with a JSON body. The JSON should contain 'fields' key-value pairs.
        'fields' is a list of dictionaries, each containing 'name' and 'type' of the field.

        Parameters:
            request: A Django REST Framework request object.
            pk: An integer representing the primary key of the table metadata.

        Returns:
            If the table does not exist, it returns an HTTP 404 Not Found status with a JSON body containing
            'detail': 'Table not found.'

            If the table is successfully updated, it returns an HTTP 200 OK status with a JSON body containing
            'detail': 'Table structure replaced.'

            If there is any validation error in the input, it returns an HTTP 400 Bad Request status with a JSON body
            containing the validation errors.
        """
        try:
            table_metadata = TableMetadata.get_by_id(table_metadata_id=pk)
        except TableMetadata.DoesNotExist:
            return Response({'detail': 'Table not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateTableSerializer(data=request.data)
        if serializer.is_valid():
            fields = serializer.validated_data['fields']

            drop_sql = f"DROP TABLE IF EXISTS {table_metadata.table_name};"
            with connection.cursor() as cursor:
                cursor.execute(drop_sql)

            table_fields = ', '.join(
                [f"{field['name']} {get_sql_field_type(field['type'])}" for field in fields]
            )

            create_sql = f"CREATE TABLE {table_metadata.table_name} (id serial PRIMARY KEY, {table_fields});"
            with connection.cursor() as cursor:
                cursor.execute(create_sql)

            table_metadata.fields = fields
            table_metadata.save()

            return Response({'detail': 'Table structure replaced.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateTableRowView(APIView):
    """
    The UpdateTableRowView is a Django REST Framework view that provides an API endpoint for adding new rows to a table
    in the database. It inherits from the APIView provided by the Django REST Framework.

    Methods:
        post: Accepts a POST request with a JSON body. The JSON should contain 'fields' key-value pairs.
              'fields' is a list of dictionaries, each containing 'name' and 'type' of the field.
              Adds new rows to the specified table as per the fields data.
              If the table does not exist, it returns an HTTP 404 Not Found status.
              If the table is successfully updated, it returns an HTTP 200 OK status.
    """

    @swagger_auto_schema(
        request_body=UpdateTableSerializer,
        operation_description="Endpoint for add rows to table in DB"
    )
    def post(self, request, pk):
        """
        Accepts a POST request with a JSON body. The JSON should contain 'fields' key-value pairs.
        'fields' is a list of dictionaries, each containing 'name' and 'type' of the field.

        Parameters:
            request: A Django REST Framework request object.
            pk: An integer representing the primary key of the table metadata.

        Returns:
            If the table does not exist, it returns an HTTP 404 Not Found status with a JSON body containing
            'detail': 'Table not found.'

            If the table is successfully updated, it returns an HTTP 200 OK status with a JSON body containing
            'detail': 'Table updated.'

            If there is any validation error in the input, it returns an HTTP 400 Bad Request status with a JSON body
            containing the validation errors.
        """
        try:
            table_metadata = TableMetadata.get_by_id(table_metadata_id=pk)
        except TableMetadata.DoesNotExist:
            return Response({'detail': 'Table not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateTableSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            fields = serializer.validated_data['fields']

            table_fields = ', '.join(
                [f"ADD COLUMN {field['name']} {get_sql_field_type(field['type'])}" for field in fields]
            )

            sql = f"ALTER TABLE {table_metadata.table_name} {table_fields};"

            with connection.cursor() as cursor:
                cursor.execute(sql)

            updated_fields = table_metadata.fields + fields
            table_metadata.fields = updated_fields
            table_metadata.save()

            return Response({'detail': 'Table updated.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableRowsView(APIView):
    """
    The TableRowsView is a Django REST Framework view that provides an API endpoint for getting all rows from a table
    in the database. It inherits from the APIView provided by the Django REST Framework.

    Methods:
        get: Accepts a GET request. Fetches all rows from the specified table.
             If the table does not exist, it returns an HTTP 404 Not Found status.
             If the rows are successfully fetched, it returns an HTTP 200 OK status along with the data.
    """

    @swagger_auto_schema(
        responses={200: FieldSerializer(many=True)},
        operation_description="Endpoint to get all rows from table in DB"
    )
    def get(self, request, pk):
        """
        Accepts a GET request. Fetches all rows from the specified table.

        Parameters:
            request: A Django REST Framework request object.
            pk: An integer representing the primary key of the table metadata.

        Returns:
            If the table does not exist, it returns an HTTP 404 Not Found status with a JSON body containing
            'detail': 'Table not found.'

            If the rows are successfully fetched, it returns an HTTP 200 OK status with a JSON body containing
            the data.
        """
        try:
            table_metadata = TableMetadata.get_by_id(table_metadata_id=pk)
        except TableMetadata.DoesNotExist:
            return Response({'detail': 'Table not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(table_metadata.fields, status=status.HTTP_200_OK)
