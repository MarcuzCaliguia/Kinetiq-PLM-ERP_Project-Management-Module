from django import template
from django.db import connection

register = template.Library()

@register.simple_tag
def get_available_ids(table_name, id_field, limit=10):
    """Get available IDs from a specified table for reference"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT {id_field} FROM {table_name} LIMIT {limit}")
            return [row[0] for row in cursor.fetchall()]
    except Exception:
        return []

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    return dictionary.get(key)