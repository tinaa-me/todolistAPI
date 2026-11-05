from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=True, methods=['patch'])
    def toggle(self, request, pk=None):
        task = self.get_object()
        if task.status == Task.Status.DONE:
            task.status = Task.Status.NOT_STARTED
        else:
            task.status = Task.Status.DONE
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)