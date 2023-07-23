from django.db import models
from django.db.models import JSONField


class TableMetadata(models.Model):
    table_name = models.CharField(max_length=255, unique=True)
    fields = JSONField()

    class Meta:
        db_table = "table_metadata"

    @classmethod
    def get_by_id(cls, table_metadata_id: int):
        return cls.objects.get(pk=table_metadata_id)

    @classmethod
    def save_entity(cls, table_name: str, fields: list[dict[str, str]]) -> None:
        cls.objects.create(table_name=table_name, fields=fields)
