
import django_filters
from .models import InternalProjectRequest, ExternalProjectRequest

class InternalProjectFilter(django_filters.FilterSet):
    class Meta:
        model = InternalProjectRequest
        fields = {
            'project_request_id': ['exact', 'contains'],
            'project_name': ['exact', 'contains'],
            'approval_id': ['exact'],
            'dept_id': ['exact'],
            'employee_id': ['exact'],
            'request_date': ['exact', 'gte', 'lte'],
            'request_starting_date': ['exact', 'gte', 'lte'],
        }

class ExternalProjectFilter(django_filters.FilterSet):
    class Meta:
        model = ExternalProjectRequest
        fields = {
            'ext_project_request_id': ['exact', 'contains'],
            'ext_project_name': ['exact', 'contains'],
            'approval_id': ['exact'],
            'item_id': ['exact'],
        }