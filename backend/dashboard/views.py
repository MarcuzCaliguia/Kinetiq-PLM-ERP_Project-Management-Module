
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from .models import (
    ExternalProjectDetails, InternalProjectDetails,
    ExternalProjectTracking, InternalProjectTracking,
    ExternalProjectTaskList, InternalProjectTaskList,
    ExternalProjectWarranty, ExternalProjectRequest,
    InternalProjectRequest
)
from .serializers import (
    ExternalProjectTrackingSerializer, InternalProjectTrackingSerializer,
    ExternalProjectTaskListSerializer, InternalProjectTaskListSerializer,
    CreateExternalProjectSerializer, CreateInternalProjectSerializer,
    ExternalProjectDetailsSerializer, InternalProjectDetailsSerializer,
    ExternalProjectWarrantySerializer, ExternalProjectRequestSerializer,
    InternalProjectRequestSerializer
)
from datetime import date
from django.db.models import Q

class OverdueTasksView(APIView):
    def get(self, request):
        
        today = date.today()
        
        external_overdue = ExternalProjectTaskList.objects.filter(task_deadline__lt=today)
        internal_overdue = InternalProjectTaskList.objects.filter(intrnl_task_deadline__lt=today)
        
        external_serializer = ExternalProjectTaskListSerializer(external_overdue, many=True)
        internal_serializer = InternalProjectTaskListSerializer(internal_overdue, many=True)
        
        
        combined_data = external_serializer.data + internal_serializer.data
        
        return Response(combined_data)

class TodayTasksView(APIView):
    def get(self, request):
        
        today = date.today()
        
        external_today = ExternalProjectTaskList.objects.filter(task_deadline=today)
        internal_today = InternalProjectTaskList.objects.filter(intrnl_task_deadline=today)
        
        external_serializer = ExternalProjectTaskListSerializer(external_today, many=True)
        internal_serializer = InternalProjectTaskListSerializer(internal_today, many=True)
        
        
        combined_data = external_serializer.data + internal_serializer.data
        
        return Response(combined_data)

class ExternalProjectTrackingView(APIView):
    def get(self, request):
        projects = ExternalProjectTracking.objects.all()
        serializer = ExternalProjectTrackingSerializer(projects, many=True)
        return Response(serializer.data)

class InternalProjectTrackingView(APIView):
    def get(self, request):
        projects = InternalProjectTracking.objects.all()
        serializer = InternalProjectTrackingSerializer(projects, many=True)
        return Response(serializer.data)

class SearchExternalProjectView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if not query:
            
            projects = ExternalProjectDetails.objects.all()[:10]
        else:
            projects = ExternalProjectDetails.objects.filter(
                project_id__icontains=query
            )[:10]
        
        serializer = ExternalProjectDetailsSerializer(projects, many=True)
        return Response(serializer.data)

class SearchInternalProjectView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if not query:
            
            projects = InternalProjectDetails.objects.all()[:10]
        else:
            projects = InternalProjectDetails.objects.filter(
                intrnl_project_id__icontains=query
            )[:10]
        
        serializer = InternalProjectDetailsSerializer(projects, many=True)
        return Response(serializer.data)

class SearchWarrantyView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if not query:
            
            warranties = ExternalProjectWarranty.objects.all()[:10]
        else:
            warranties = ExternalProjectWarranty.objects.filter(
                project_warranty_id__icontains=query
            )[:10]
        
        serializer = ExternalProjectWarrantySerializer(warranties, many=True)
        return Response(serializer.data)

class SearchProjectRequestView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if not query:
            
            requests = InternalProjectRequest.objects.all()[:10]
        else:
            requests = InternalProjectRequest.objects.filter(
                Q(project_request_id__icontains=query) | Q(project_name__icontains=query)
            )[:10]
        
        serializer = InternalProjectRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
class CreateExternalProjectView(APIView):
    def post(self, request):
        serializer = CreateExternalProjectSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateInternalProjectView(APIView):
    def post(self, request):
        serializer = CreateInternalProjectSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectSummaryView(APIView):
    def get(self, request):
        try:
            
            external_projects = ExternalProjectTracking.objects.all()
            
            
            internal_projects = InternalProjectTracking.objects.all()
            
            
            combined_data = []
            
            
            for project in external_projects:
                combined_data.append({
                    'id': project.project_tracking_id,
                    'projectId': project.project.project_id if project.project else "N/A",
                    'type': 'External',
                    'startDate': project.start_date.strftime('%Y-%m-%d') if project.start_date else "N/A",
                    'endDate': project.estimated_end_date.strftime('%Y-%m-%d') if project.estimated_end_date else "N/A",
                    'issue': project.project_issue if project.project_issue else ""
                })
            
            
            for project in internal_projects:
                combined_data.append({
                    'id': project.intrnl_project_tracking_id,
                    'projectId': project.intrnl_project.intrnl_project_id if project.intrnl_project else "N/A",
                    'type': 'Internal',
                    'startDate': project.intrnl_start_date.strftime('%Y-%m-%d') if project.intrnl_start_date else "N/A",
                    'endDate': project.intrnl_estimated_end_date.strftime('%Y-%m-%d') if project.intrnl_estimated_end_date else "N/A",
                    'issue': project.intrnl_project_issue if project.intrnl_project_issue else ""
                })
            
            return Response(combined_data)
        except Exception as e:
            print(f"Error in ProjectSummaryView: {str(e)}")
            return Response({"error": str(e)}, status=500)