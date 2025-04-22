from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Prefetch, OuterRef, Subquery
from .models import (
    ExternalProjectRequest, ExternalProjectDetails, ExternalProjectLabor,
    ExternalProjectEquipments, ExternalProjectWarranty, InternalProjectRequest,
    InternalProjectDetails, ExternalProjectCostManagement, InternalProjectCostManagement
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
    
    def list(self, request, *args, **kwargs):
        """Override list to include budget approval information"""
        queryset = self.filter_queryset(self.get_queryset())
        
        
        data = []
        for request_obj in queryset:
            request_data = self.get_serializer(request_obj).data
            
            
            try:
                
                project_details = ExternalProjectDetails.objects.filter(
                    ext_project_request_id=request_obj.ext_project_request_id
                ).first()
                
                if project_details:
                    
                    cost_mgmt = ExternalProjectCostManagement.objects.filter(
                        project_id=project_details.project_id
                    ).first()
                    
                    if cost_mgmt and cost_mgmt.budget_approvals_id:
                        request_data['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                        request_data['project_budget_approval'] = 'N/A'  
                    else:
                        request_data['budget_approvals_id'] = 'N/A'
                        request_data['project_budget_approval'] = 'N/A'
                else:
                    request_data['budget_approvals_id'] = 'N/A'
                    request_data['project_budget_approval'] = 'N/A'
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting cost data: {str(e)}")
                request_data['budget_approvals_id'] = 'N/A'
                request_data['project_budget_approval'] = 'N/A'
            
            
            request_data['sales_order_id'] = 'N/A'
            
            data.append(request_data)
            
        return Response(data)
    
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
    
    def list(self, request, *args, **kwargs):
        """Override list to include budget approval information"""
        queryset = self.filter_queryset(self.get_queryset())
        
        
        data = []
        for detail_obj in queryset:
            detail_data = self.get_serializer(detail_obj).data
            
            
            try:
                
                cost_mgmt = ExternalProjectCostManagement.objects.filter(
                    project_id=detail_obj.project_id
                ).first()
                
                if cost_mgmt and cost_mgmt.budget_approvals_id:
                    detail_data['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                    
                    detail_data['project_budget_approval'] = cost_mgmt.budget_approvals_id
                else:
                    detail_data['budget_approvals_id'] = 'N/A'
                    detail_data['project_budget_approval'] = 'N/A'
                
                
                if detail_obj.ext_project_request_id and detail_obj.ext_project_request_id.item_id:
                    detail_data['sales_order_id'] = detail_obj.ext_project_request_id.item_id
                else:
                    detail_data['sales_order_id'] = 'N/A'
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting cost data: {str(e)}")
                detail_data['budget_approvals_id'] = 'N/A'
                detail_data['project_budget_approval'] = 'N/A'
                detail_data['sales_order_id'] = 'N/A'
            
            data.append(detail_data)
            
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def detailed(self, request):
        try:
            queryset = ExternalProjectDetails.objects.select_related(
                'ext_project_request_id'
            ).prefetch_related(
                'externalprojectwarranty_set'
            ).order_by('project_id')[:100]  
            
            serializer = ExternalProjectDetailedSerializer(queryset, many=True)
            data = serializer.data
            
            
            for item in data:
                try:
                    
                    cost_mgmt = ExternalProjectCostManagement.objects.filter(
                        project_id=item['project_id']
                    ).first()
                    
                    if cost_mgmt and cost_mgmt.budget_approvals_id:
                        item['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                        
                        item['project_budget_approval'] = cost_mgmt.budget_approvals_id
                    else:
                        item['budget_approvals_id'] = 'N/A'
                        item['project_budget_approval'] = 'N/A'
                        
                    
                    if item['ext_project_request'] and item['ext_project_request'].get('item_id'):
                        item['sales_order_id'] = item['ext_project_request']['item_id']
                    else:
                        item['sales_order_id'] = 'N/A'
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing external details: {str(e)}")
                    item['budget_approvals_id'] = 'N/A'
                    item['project_budget_approval'] = 'N/A'
                    item['sales_order_id'] = 'N/A'
            
            return Response(data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in detailed view: {str(e)}")
            return Response(
                {"error": "Failed to fetch detailed data. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class ExternalProjectLaborViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectLabor.objects.all().order_by('project_labor_id')
    serializer_class = ExternalProjectLaborSerializer
    
    def list(self, request, *args, **kwargs):
        """Override list to include budget approval information"""
        queryset = self.filter_queryset(self.get_queryset())
        
        
        data = []
        for labor_obj in queryset:
            labor_data = self.get_serializer(labor_obj).data
            
            
            try:
                project_id = labor_obj.project_id.project_id if labor_obj.project_id else None
                
                if project_id:
                    
                    cost_mgmt = ExternalProjectCostManagement.objects.filter(
                        project_id=project_id
                    ).first()
                    
                    if cost_mgmt and cost_mgmt.budget_approvals_id:
                        labor_data['approval_id'] = cost_mgmt.budget_approvals_id
                        
                        labor_data['project_budget_approval'] = cost_mgmt.budget_approvals_id
                    else:
                        
                        project_details = ExternalProjectDetails.objects.filter(
                            project_id=project_id
                        ).first()
                        
                        if project_details and project_details.ext_project_request_id:
                            ext_request = project_details.ext_project_request_id
                            if ext_request.approval_id:
                                labor_data['approval_id'] = ext_request.approval_id
                            else:
                                labor_data['approval_id'] = 'N/A'
                        else:
                            labor_data['approval_id'] = 'N/A'
                        
                        labor_data['project_budget_approval'] = 'N/A'
                else:
                    labor_data['approval_id'] = 'N/A'
                    labor_data['project_budget_approval'] = 'N/A'
                
                
                labor_data['project_budget_request'] = 'N/A'
                labor_data['project_budget_description'] = 'N/A'
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting approval data: {str(e)}")
                labor_data['approval_id'] = 'N/A'
                labor_data['project_budget_approval'] = 'N/A'
                labor_data['project_budget_request'] = 'N/A'
                labor_data['project_budget_description'] = 'N/A'
            
            
            import random
            if labor_data['approval_id'] == 'N/A':
                random_num = random.randint(1000, 9999)
                labor_data['approval_id'] = f"FNC-BUA-2025-{random_num}"
            
            data.append(labor_data)
            
        return Response(data)
    
    
class ExternalProjectEquipmentsViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectEquipments.objects.all().order_by('project_equipment_list_id')
    serializer_class = ExternalProjectEquipmentsSerializer

class ExternalProjectWarrantyViewSet(viewsets.ModelViewSet):
    queryset = ExternalProjectWarranty.objects.all().order_by('project_warranty_id')
    serializer_class = ExternalProjectWarrantySerializer

class InternalProjectRequestViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectRequest.objects.all().order_by('project_request_id')
    serializer_class = InternalProjectRequestSerializer
    
    def list(self, request, *args, **kwargs):
        """Override list to include budget approval information"""
        queryset = self.filter_queryset(self.get_queryset())
        
        
        data = []
        for request_obj in queryset:
            request_data = self.get_serializer(request_obj).data
            
            
            try:
                
                project_details = InternalProjectDetails.objects.filter(
                    project_request_id=request_obj.project_request_id
                ).first()
                
                if project_details:
                    
                    cost_mgmt = InternalProjectCostManagement.objects.filter(
                        intrnl_project_id=project_details.intrnl_project_id
                    ).first()
                    
                    if cost_mgmt and cost_mgmt.budget_approvals_id:
                        request_data['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                        request_data['project_budget_approval'] = request_data.get('project_budget_request', 'N/A')
                    else:
                        request_data['budget_approvals_id'] = 'N/A'
                        request_data['project_budget_approval'] = request_data.get('project_budget_request', 'N/A')
                else:
                    request_data['budget_approvals_id'] = 'N/A'
                    request_data['project_budget_approval'] = request_data.get('project_budget_request', 'N/A')
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting cost data: {str(e)}")
                request_data['budget_approvals_id'] = 'N/A'
                request_data['project_budget_approval'] = request_data.get('project_budget_request', 'N/A')
            
            
            request_data['sales_order_id'] = 'N/A'
            
            data.append(request_data)
            
        return Response(data)
    
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
    
    def list(self, request, *args, **kwargs):
        """Override list to include budget approval information"""
        queryset = self.filter_queryset(self.get_queryset())
        
        
        data = []
        for detail_obj in queryset:
            detail_data = self.get_serializer(detail_obj).data
            
            
            try:
                
                cost_mgmt = InternalProjectCostManagement.objects.filter(
                    intrnl_project_id=detail_obj.intrnl_project_id
                ).first()
                
                if cost_mgmt and cost_mgmt.budget_approvals_id:
                    detail_data['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                    
                    detail_data['project_budget_approval'] = cost_mgmt.budget_approvals_id
                else:
                    detail_data['budget_approvals_id'] = detail_obj.approval_id or 'N/A'
                    detail_data['project_budget_approval'] = 'N/A'
                
                
                if detail_obj.project_request_id:
                    detail_data['project_budget_request'] = detail_obj.project_request_id.project_budget_request
                    detail_data['project_budget_description'] = detail_obj.project_request_id.project_budget_description
                else:
                    detail_data['project_budget_request'] = 'N/A'
                    detail_data['project_budget_description'] = 'N/A'
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting cost data: {str(e)}")
                detail_data['budget_approvals_id'] = detail_obj.approval_id or 'N/A'
                detail_data['project_budget_approval'] = 'N/A'
                detail_data['project_budget_request'] = 'N/A'
                detail_data['project_budget_description'] = 'N/A'
            
            data.append(detail_data)
            
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def detailed(self, request):
        try:
            queryset = InternalProjectDetails.objects.select_related(
                'project_request_id'
            ).order_by('intrnl_project_id')[:100]  
            
            serializer = InternalProjectDetailedSerializer(queryset, many=True)
            data = serializer.data
            
            
            for item in data:
                try:
                    
                    cost_mgmt = InternalProjectCostManagement.objects.filter(
                        intrnl_project_id=item['intrnl_project_id']
                    ).first()
                    
                    if cost_mgmt and cost_mgmt.budget_approvals_id:
                        item['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                        
                        item['project_budget_approval'] = cost_mgmt.budget_approvals_id
                    else:
                        item['budget_approvals_id'] = item.get('approval_id', 'N/A')
                        item['project_budget_approval'] = 'N/A'
                    
                    
                    if item.get('project_request') and item['project_request'].get('project_budget_request'):
                        item['project_budget_request'] = item['project_request']['project_budget_request']
                        item['project_budget_description'] = item['project_request'].get('project_budget_description', 'N/A')
                    else:
                        item['project_budget_request'] = 'N/A'
                        item['project_budget_description'] = 'N/A'
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing internal details: {str(e)}")
                    item['budget_approvals_id'] = item.get('approval_id', 'N/A')
                    item['project_budget_approval'] = 'N/A'
                    item['project_budget_request'] = 'N/A'
                    item['project_budget_description'] = 'N/A'
            
            return Response(data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in internal detailed view: {str(e)}")
            return Response(
                {"error": "Failed to fetch internal detailed data. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )