from medical.models import Item
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from api_fhir_r4.permissions import FHIRApiMedicationPermissions
from api_fhir_r4.serializers import MedicationSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class MedicationViewSet(BaseFHIRView, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'uuid'
    serializer_class = MedicationSerializer
    permission_classes = (FHIRApiMedicationPermissions,)

    def get_queryset(self):
        return Item.get_queryset(None, self.request.user)
