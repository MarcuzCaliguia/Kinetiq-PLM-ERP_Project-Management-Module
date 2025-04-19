from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Prefetch
from .models import (
    ExternalProjectRequest, ExternalProjectDetails, ExternalProjectLabor,
    ExternalProjectEquipments, ExternalProjectWarranty, InternalProjectRequest,
    InternalProjectDetails
)
from .serializers import (
    ExternalProjectRequestSerializer, ExternalProjectDetailsSerializer,
    ExternalProjectLaborSerializer, ExternalProjectEquipmentsSerializer,
    ExternalProjectWarrantySerializer, InternalProjectRequestSerializer,
    InternalProjectDetailsSerializer, ExternalProjectDetailedSerializer,
    InternalProjectDetailedSerializer
)

class ExternalProjectRequestViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectRequest.objects.all()
    serializer_class = ExternalProjectRequestSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        ExternalProjectRequest.objects.filter(ext_project_request_id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExternalProjectDetailsViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectDetails.objects.all().order_by('project_id')
    serializer_class = ExternalProjectDetailsSerializer
    
    @action(detail=False, methods=['get'])
    def detailed(self, request):
        try:
            # Optimize query with prefetch_related to avoid N+1 queries
            queryset = ExternalProjectDetails.objects.select_related(
                'ext_project_request_id'
            ).prefetch_related(
                'externalprojectwarranty_set'
            ).order_by('project_id')[:100]  # Limit to 100 records for performance
            
            serializer = ExternalProjectDetailedSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            # Log the error and return a friendly message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in detailed view: {str(e)}")
            return Response(
                {"error": "Failed to fetch detailed data. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        ExternalProjectDetails.objects.filter(project_id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExternalProjectLaborViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectLabor.objects.all().order_by('project_labor_id')
    serializer_class = ExternalProjectLaborSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        ExternalProjectLabor.objects.filter(project_labor_id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExternalProjectEquipmentsViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectEquipments.objects.all().order_by('project_equipment_list_id')
    serializer_class = ExternalProjectEquipmentsSerializer

class ExternalProjectWarrantyViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectWarranty.objects.all().order_by('project_warranty_id')
    serializer_class = ExternalProjectWarrantySerializer

class InternalProjectRequestViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectRequest.objects.all().order_by('project_request_id')
    serializer_class = InternalProjectRequestSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"error": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        InternalProjectRequest.objects.filter(project_request_id__in=ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InternalProjectDetailsViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectDetails.objects.all().order_by('intrnl_project_id')
    serializer_class = InternalProjectDetailsSerializer
    
    @action(detail=False, methods=['get'])
    def detailed(self, request):
        try:
            # Optimize query with select_related to avoid N+1 queries
            queryset = InternalProjectDetails.objects.select_related(
                'project_request_id'
            ).order_by('intrnl_project_id')[:100]  # Limit to 100 records for performance
            
            serializer = InternalProjectDetailedSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            # Log the error and return a friendly message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in internal detailed view: {str(e)}")
            return Response(
                {"error": "Failed to fetch internal detailed data. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )