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

import datetime 
from decimal import Decimal

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
                # Get approval_id directly from the request object
                approval_id = request_obj.approval_id
                request_data['approval_id'] = approval_id if approval_id else 'N/A'
                
                # Add more data from the request object
                request_data['ext_project_name'] = request_obj.ext_project_name
                request_data['ext_project_description'] = request_obj.ext_project_description
                
                project_details = ExternalProjectDetails.objects.filter(
                    ext_project_request_id=request_obj.ext_project_request_id
                ).first()
                
                if project_details:
                    request_data['project_id'] = project_details.project_id
                    request_data['project_status'] = project_details.project_status
                    
                    cost_mgmt = ExternalProjectCostManagement.objects.filter(
                        project_id=project_details.project_id
                    ).first()
                    
                    if cost_mgmt and cost_mgmt.budget_approvals_id:
                        request_data['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                        request_data['project_budget_approval'] = cost_mgmt.budget_approvals_id
                    else:
                        request_data['budget_approvals_id'] = 'N/A'
                        request_data['project_budget_approval'] = 'N/A'
                else:
                    request_data['project_id'] = 'N/A'
                    request_data['project_status'] = 'Not Started'
                    request_data['budget_approvals_id'] = 'N/A'
                    request_data['project_budget_approval'] = 'N/A'
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting data: {str(e)}")
                request_data['approval_id'] = 'N/A'
                request_data['budget_approvals_id'] = 'N/A'
                request_data['project_budget_approval'] = 'N/A'
                request_data['project_status'] = 'N/A'
            
            request_data['sales_order_id'] = request_obj.item_id if request_obj.item_id else 'N/A'
            
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
                # Get management approval ID
                if detail_obj.ext_project_request_id:
                    detail_data['approval_id'] = detail_obj.ext_project_request_id.approval_id if detail_obj.ext_project_request_id.approval_id else 'N/A'
                else:
                    detail_data['approval_id'] = 'N/A'
                
                # Get finance budget approval ID
                cost_mgmt = ExternalProjectCostManagement.objects.filter(
                    project_id=detail_obj.project_id
                ).first()
                
                if cost_mgmt and cost_mgmt.budget_approvals_id:
                    detail_data['project_budget_approval'] = cost_mgmt.budget_approvals_id
                    detail_data['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                else:
                    detail_data['project_budget_approval'] = 'N/A'
                    detail_data['budget_approvals_id'] = 'N/A'
                
                # Get sales order ID
                if detail_obj.ext_project_request_id and detail_obj.ext_project_request_id.item_id:
                    detail_data['sales_order_id'] = detail_obj.ext_project_request_id.item_id
                else:
                    detail_data['sales_order_id'] = 'N/A'
                
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error getting data: {str(e)}")
                detail_data['approval_id'] = 'N/A'
                detail_data['project_budget_approval'] = 'N/A'
                detail_data['budget_approvals_id'] = 'N/A'
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
                    # Get management approval ID
                    if item['ext_project_request'] and 'approval_id' in item['ext_project_request']:
                        item['approval_id'] = item['ext_project_request']['approval_id'] or 'N/A'
                    else:
                        item['approval_id'] = 'N/A'
                    
                    # Get finance budget approval ID
                    cost_mgmt = ExternalProjectCostManagement.objects.filter(
                        project_id=item['project_id']
                    ).first()
                    
                    if cost_mgmt and cost_mgmt.budget_approvals_id:
                        item['project_budget_approval'] = cost_mgmt.budget_approvals_id
                        item['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                    else:
                        item['project_budget_approval'] = 'N/A'
                        item['budget_approvals_id'] = 'N/A'
                    
                    # Get sales order ID
                    if item['ext_project_request'] and 'item_id' in item['ext_project_request']:
                        item['sales_order_id'] = item['ext_project_request']['item_id'] or 'N/A'
                    else:
                        item['sales_order_id'] = 'N/A'
                    
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error processing external details: {str(e)}")
                    item['approval_id'] = 'N/A'
                    item['project_budget_approval'] = 'N/A'
                    item['budget_approvals_id'] = 'N/A'
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
                    # Get management approval ID
                    project_details = ExternalProjectDetails.objects.filter(
                        project_id=project_id
                    ).first()
                    
                    if project_details and project_details.ext_project_request_id:
                        ext_request = project_details.ext_project_request_id
                        labor_data['approval_id'] = ext_request.approval_id or 'N/A'
                    else:
                        labor_data['approval_id'] = 'N/A'
                    
                    # Get finance budget approval ID
                    cost_mgmt = ExternalProjectCostManagement.objects.filter(
                        project_id=project_id
                    ).first()
                    
                    if cost_mgmt and cost_mgmt.budget_approvals_id:
                        labor_data['project_budget_approval'] = cost_mgmt.budget_approvals_id
                    else:
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
        """Override list to include budget approval information and dept_id"""
        from django.db import connection
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("Executing InternalProjectRequestViewSet.list with direct SQL")
        
        # Helper function to convert cursor results to dictionaries
        def dictfetchall(cursor):
            """Return all rows from a cursor as a dict"""
            columns = [col[0] for col in cursor.description]
            return [
                {columns[i]: value for i, value in enumerate(row)}
                for row in cursor.fetchall()
            ]
        
        # Helper function to convert dates and decimals for JSON serialization
        def serialize_result(data):
            """Convert dates and decimals to strings for JSON serialization"""
            for item in data:
                for key, value in item.items():
                    if isinstance(value, datetime.date):
                        item[key] = value.isoformat()
                    elif isinstance(value, Decimal):
                        item[key] = float(value)
                    # Make sure empty strings or None values are handled properly
                    elif value is None:
                        item[key] = 'N/A'
            return data
        
        try:
            # Get base data from internal_project_request, now including department_name
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                    ipr.project_request_id, 
                    ipr.project_name, 
                    ipr.project_description, 
                    ipr.request_date, 
                    ipr.target_starting_date, 
                    ipr.employee_id, 
                    ipr.dept_id, 
                    d.dept_name AS department_name,
                    ipr.project_budget_request, 
                    ipr.project_budget_description
                FROM 
                    project_management.internal_project_request ipr
                LEFT JOIN 
                    human_resources.departments d ON ipr.dept_id = d.dept_id
                ORDER BY 
                    ipr.project_request_id
                """)
                base_data = dictfetchall(cursor)
                
                # Log some sample data to check if project_name is present
                logger.info(f"Raw base data sample (first 3 records):")
                for i, record in enumerate(base_data[:3]):
                    logger.info(f"Record {i}: project_request_id={record.get('project_request_id')}, project_name={record.get('project_name')}")
            
            # Convert dates and decimals for JSON serialization
            base_data = serialize_result(base_data)
            
            # Process each record to add budget approval information
            for item in base_data:
                try:
                    # Ensure project_name is properly handled
                    if 'project_name' not in item or item['project_name'] is None or item['project_name'] == '':
                        item['project_name'] = 'N/A'
                    
                    # Get related project details if any
                    project_details = InternalProjectDetails.objects.filter(
                        project_request_id=item['project_request_id']
                    ).first()
                    
                    if project_details:
                        # Get finance budget approval ID
                        cost_mgmt = InternalProjectCostManagement.objects.filter(
                            intrnl_project_id=project_details.intrnl_project_id
                        ).first()
                        
                        if cost_mgmt and cost_mgmt.budget_approvals_id:
                            item['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                            item['project_budget_approval'] = cost_mgmt.budget_approvals_id
                        else:
                            item['budget_approvals_id'] = 'N/A'
                            item['project_budget_approval'] = 'N/A'
                    else:
                        item['budget_approvals_id'] = 'N/A'
                        item['project_budget_approval'] = 'N/A'
                    
                    # Ensure dept_id is properly handled
                    if 'dept_id' not in item or item['dept_id'] is None:
                        item['dept_id'] = 'N/A'
                    
                except Exception as e:
                    logger.error(f"Error processing record {item.get('project_request_id')}: {str(e)}")
                    item['budget_approvals_id'] = 'N/A'
                    item['project_budget_approval'] = 'N/A'
                    if 'dept_id' not in item or item['dept_id'] is None:
                        item['dept_id'] = 'N/A'
            
            # Log the final processed data
            logger.info(f"Final processed data sample (first 3 records):")
            for i, record in enumerate(base_data[:3]):
                logger.info(f"Record {i}: project_request_id={record.get('project_request_id')}, project_name={record.get('project_name')}, dept_id={record.get('dept_id')}, department_name={record.get('department_name')}")
            
            return Response(base_data)
            
        except Exception as e:
            logger.error(f"Error in list method: {str(e)}")
            return Response(
                {"error": f"Failed to fetch internal project requests: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
                # Get management approval ID
                detail_data['approval_id'] = detail_obj.approval_id or 'N/A'
                
                # Get finance budget approval ID
                cost_mgmt = InternalProjectCostManagement.objects.filter(
                    intrnl_project_id=detail_obj.intrnl_project_id
                ).first()
                
                if cost_mgmt and cost_mgmt.budget_approvals_id:
                    detail_data['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                    detail_data['project_budget_approval'] = cost_mgmt.budget_approvals_id
                else:
                    detail_data['budget_approvals_id'] = 'N/A'
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
                detail_data['approval_id'] = 'N/A'
                detail_data['budget_approvals_id'] = 'N/A'
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
                    # Get management approval ID
                    item['approval_id'] = item.get('approval_id') or 'N/A'
                    
                    # Get finance budget approval ID
                    cost_mgmt = InternalProjectCostManagement.objects.filter(
                        intrnl_project_id=item['intrnl_project_id']
                    ).first()
                    
                    if cost_mgmt and cost_mgmt.budget_approvals_id:
                        item['budget_approvals_id'] = cost_mgmt.budget_approvals_id
                        item['project_budget_approval'] = cost_mgmt.budget_approvals_id
                    else:
                        item['budget_approvals_id'] = 'N/A'
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
                    item['approval_id'] = 'N/A'
                    item['budget_approvals_id'] = 'N/A'
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