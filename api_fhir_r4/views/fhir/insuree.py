import datetime

from claim.models import Claim
from insuree.models import Insuree

from django.db.models import OuterRef, Exists
from rest_framework import viewsets, status
from rest_framework.response import Response

from api_fhir_r4.converters import OperationOutcomeConverter
from api_fhir_r4.permissions import FHIRApiInsureePermissions
from api_fhir_r4.serializers import PatientSerializer
from api_fhir_r4.views.fhir.fhir_base_viewset import BaseFHIRView


class InsureeViewSet(BaseFHIRView, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    serializer_class = PatientSerializer
    permission_classes = (FHIRApiInsureePermissions,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()\
            .select_related('gender')\
            .select_related('photo')\
            .select_related('family__location')
        ref_date_str = request.GET.get('refDate')
        claim_date = request.GET.get('claimDateFrom')
        identifier = request.GET.get("identifier")
        if identifier:
            queryset = queryset.filter(chf_id=identifier)
        else:
            queryset = queryset.filter(validity_to__isnull=True).order_by('validity_from')
            if ref_date_str is not None:
                try:
                    ref_date = datetime.datetime.strptime(ref_date_str, "%Y-%m-%d").date()
                    queryset = queryset.filter(validity_from__gte=ref_date)
                except ValueError:
                    pass
            if claim_date is not None:
                try:
                    claim_parse_dated = datetime.datetime.strptime(claim_date, "%Y-%m-%d").date()
                except ValueError:
                    result = OperationOutcomeConverter\
                        .build_for_400_bad_request("claimDateFrom should be in dd-mm-yyyy format")
                    return Response(result.dict(), status.HTTP_400_BAD_REQUEST)
                has_claim_in_range = Claim.objects\
                    .filter(date_claimed__gte=claim_parse_dated)\
                    .filter(insuree_id=OuterRef("id"))\
                    .values("id")
                queryset = queryset\
                    .annotate(has_claim_in_range=Exists(has_claim_in_range))\
                    .filter(has_claim_in_range=True)

        serializer = PatientSerializer(self.paginate_queryset(queryset), many=True)
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        return Insuree.get_queryset(None, self.request.user)
