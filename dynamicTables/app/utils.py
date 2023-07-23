def get_sql_field_type(field_type):
    if field_type == 'string':
        return 'varchar(255)'
    elif field_type == 'integer':
        return 'integer'
    elif field_type == 'boolean':
        return 'boolean'
    else:
        return 'text'
