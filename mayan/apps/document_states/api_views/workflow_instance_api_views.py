from django.shortcuts import get_object_or_404

from mayan.apps.acls.models import AccessControlList
from mayan.apps.converter.api_view_mixins import APIImageViewMixin
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.permissions import permission_document_type_view
from mayan.apps.documents.serializers.document_type_serializers import DocumentTypeSerializer
from mayan.apps.rest_api.api_view_mixins import ExternalObjectAPIViewMixin
from mayan.apps.rest_api import generics

from ..models.workflow_models import Workflow
from ..permissions import (
    permission_workflow_instance_transition,
    permission_workflow_template_create, permission_workflow_template_delete,
    permission_workflow_template_edit, permission_workflow_template_view
)
from ..serializers import (
    WorkflowInstanceSerializer, WorkflowInstanceLogEntrySerializer,
    WorkflowTemplateDocumentTypeAddSerializer,
    WorkflowTemplateDocumentTypeRemoveSerializer, WorkflowTemplateSerializer,
    WorkflowTemplateStateSerializer, WorkflowTemplateTransitionSerializer,
    WorkflowTransitionFieldSerializer
)

# Document workflow views

class APIWorkflowInstanceListView(
    ExternalObjectAPIViewMixin, generics.ListAPIView
):
    """
    get: Returns a list of all the document workflow instances.
    """
    external_object_queryset = Document.valid
    external_object_pk_url_kwarg = 'document_id'
    mayan_external_object_permissions = {
        'GET': (permission_workflow_template_view,),
    }
    mayan_object_permissions = {
        'GET': (permission_workflow_template_view,),
    }
    serializer_class = WorkflowInstanceSerializer

    def get_queryset(self):
        return self.external_object.workflows.all()


class APIWorkflowInstanceDetailView(
    ExternalObjectAPIViewMixin, generics.RetrieveAPIView
):
    """
    get: Return the details of the selected document workflow instances.
    """
    external_object_queryset = Document.valid
    external_object_pk_url_kwarg = 'document_id'
    lookup_url_kwarg = 'workflow_instance_id'
    mayan_external_object_permissions = {
        'GET': (permission_workflow_template_view,),
    }
    mayan_object_permissions = {
        'GET': (permission_workflow_template_view,),
    }
    serializer_class = WorkflowInstanceSerializer

    def get_queryset(self):
        return self.external_object.workflows.all()


class APIWorkflowInstanceLogEntryDetailView(
    ExternalObjectAPIViewMixin, generics.RetrieveAPIView
):
    """
    get: Return the details of the selected document instances log entry.
    """
    external_object_pk_url_kwarg = 'document_id'
    external_object_queryset = Document.valid
    mayan_external_object_permissions = {
        'GET': (permission_workflow_template_view,),
    }
    serializer_class = WorkflowInstanceLogEntrySerializer
    lookup_url_kwarg = 'workflow_instance_log_entry_id'

    def get_queryset(self):
        return self.get_workflow_instance().log_entries.all()

    def get_workflow_instance(self):
        workflow = get_object_or_404(
            klass=self.external_object.workflows,
            pk=self.kwargs['workflow_instance_id']
        )

        return workflow


class APIWorkflowInstanceLogEntryListView(
    ExternalObjectAPIViewMixin, generics.ListCreateAPIView
):
    """
    get: Returns a list of all the document workflow instances log entries.
    post: Transition a document workflow by creating a new document workflow instance log entry.
    """
    external_object_pk_url_kwarg = 'document_id'
    external_object_queryset = Document.valid
    mayan_external_object_permissions = {
        'GET': (permission_workflow_template_view,),
        'POST': (permission_workflow_instance_transition,),
    }
    mayan_object_permissions = {
        'GET': (permission_workflow_template_view,),
    }
    ordering_fields = (
        'comment', 'id', 'transition', 'transition__destination_state',
        'transition__origin_state'
    )
    serializer_class = WorkflowInstanceLogEntrySerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'workflow_instance': self.get_workflow_instance(),
                }
            )

        return context

    def get_queryset(self):
        return self.get_workflow_instance().log_entries.all()

    def get_workflow_instance(self):
        workflow = get_object_or_404(
            klass=self.external_object.workflows,
            pk=self.kwargs['workflow_instance_id']
        )

        return workflow


class APIWorkflowInstanceLogEntryTransitionListView(
    ExternalObjectAPIViewMixin, generics.ListAPIView
):
    """
    get: Returns a list of all the possible transition choices for the workflow instance.
    """
    external_object_pk_url_kwarg = 'document_id'
    external_object_queryset = Document.valid
    mayan_external_object_permissions = {
        'GET': (permission_workflow_template_view,),
    }
    mayan_object_permissions = {
        'GET': (permission_workflow_template_view,),
    }
    ordering_fields = ('destination_state', 'id', 'origin_state')
    serializer_class = WorkflowTemplateTransitionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.kwargs:
            context.update(
                {
                    'workflow_instance': self.get_workflow_instance(),
                }
            )

        return context

    def get_queryset(self):
        return self.get_workflow_instance().get_transition_choices(
            _user=self.request.user
        )

    def get_workflow_instance(self):
        workflow = get_object_or_404(
            klass=self.external_object.workflows,
            pk=self.kwargs['workflow_instance_id']
        )

        return workflow
