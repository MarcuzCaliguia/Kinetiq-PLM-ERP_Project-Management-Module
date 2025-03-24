from rest_framework import viewsets
from .models import (
    InternalProjectRequest,
    InternalProjectDetails,
    InternalProjectLabor,
    InternalProjectTaskList
)
from .serializers import (
    InternalProjectRequestSerializer,
    InternalProjectDetailsSerializer,
    InternalProjectLaborSerializer,
    InternalProjectTaskListSerializer
)

class InternalProjectRequestViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectRequest.objects.all()
    serializer_class = InternalProjectRequestSerializer

class InternalProjectDetailsViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectDetails.objects.all()
    serializer_class = InternalProjectDetailsSerializer

class InternalProjectLaborViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectLabor.objects.all()
    serializer_class = InternalProjectLaborSerializer

class InternalProjectTaskListViewSet(viewsets.ModelViewSet):
    queryset = InternalProjectTaskList.objects.all()
    serializer_class = InternalProjectTaskListSerializer