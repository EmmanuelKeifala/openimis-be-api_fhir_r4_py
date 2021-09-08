from api_fhir_r4.serializers import CodeSystemSerializer

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from rest_framework.views import APIView
from api_fhir_r4.views import CsrfExemptSessionAuthentication


class CodeSystemOpenIMISOrganizationLegalFormViewSet(viewsets.ViewSet):

    serializer_class = CodeSystemSerializer
    permission_classes = (AllowAny,)
    authentication_classes = [CsrfExemptSessionAuthentication] + APIView.settings.DEFAULT_AUTHENTICATION_CLASSES

    def list(self, request):
        # we don't use typical instance, we only indicate the model and the field to be mapped into CodeSystem
        serializer = CodeSystemSerializer(
            instance=None,
            **{
                "model_name": 'HealthFacilityLegalForm',
                "code_field": 'code',
                "display_field": 'legal_form',
                "id": 'openIMISOrganizationLegalForm',
                "name": 'openIMISOrganizationLegalForm',
                "title": 'openIMIS Organization Legal Form',
                "description": "Indicates the legal forms of the Organization. "
                               "Values defined by openIMIS. Can be extended.",
                "url": self.request.build_absolute_uri()
            }
        )
        data = serializer.to_representation(obj=None)
        return Response(data)
