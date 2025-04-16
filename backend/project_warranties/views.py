import uuid
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.db.models import Q

# Import both models
from .models import ExternalProjectWarranty, ExternalProjectDetails
from .serializers import ExternalProjectWarrantySerializer

class ExternalProjectWarrantyViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectWarranty.objects.all().order_by('project_warranty_id')
    serializer_class = ExternalProjectWarrantySerializer
    
    def create(self, request, *args, **kwargs):
        """Override create to generate a project_warranty_id"""
        print("Received warranty data:", request.data)
        data = request.data.copy()
        
        if 'project_warranty_id' not in data or not data['project_warranty_id']:
            year = data.get('warranty_start_date', '')[:4]  # Extract year from start date
            if not year:
                from datetime import datetime
                year = datetime.now().year
                
            random_suffix = uuid.uuid4().hex[:6]
            data['project_warranty_id'] = f"PROJ-EPW-{year}-{random_suffix}"
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        ExternalProjectWarranty.objects.filter(project_warranty_id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def project_autocomplete(request):
    query = request.GET.get('query', '')
    print(f"Project autocomplete query: {query}")
    
    if not query:
        print("No query provided, returning empty list")
        return Response([])
    
    try:
        projects = ExternalProjectDetails.objects.filter(
            project_id__icontains=query
        ).values('project_id')
        
        print(f"Found {len(projects)} projects matching query: {query}")
        
        formatted_projects = []
        for project in projects:
            formatted_projects.append({
                'project_id': project['project_id'],
                'project_name': f"Project {project['project_id']}"
            })
        
        return Response(formatted_projects)
    except Exception as e:
        print(f"Error in project_autocomplete: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)