from rest_framework import serializers

from dynamicTables.app.models import TableMetadata


class FieldSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=['string', 'number', 'boolean'])

    def validate_name(self, value):
        request = self.context.get('request', None)
        if request:
            table_id = request.parser_context['kwargs']['pk']
            table_metadata = TableMetadata.get_by_id(table_metadata_id=table_id)
            existing_field_names = [field['name'] for field in table_metadata.fields]
            if value in existing_field_names:
                raise serializers.ValidationError(f"Field with this '{value}' name already exists.")
        return value


class DynamicTableSerializer(serializers.Serializer):
    table_name = serializers.CharField(max_length=255)
    fields = FieldSerializer(many=True)


class UpdateTableSerializer(serializers.Serializer):
    fields = FieldSerializer(many=True)
