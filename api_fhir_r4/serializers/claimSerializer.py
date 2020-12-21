from claim import ClaimSubmitService, ClaimSubmit, ClaimConfig
from claim.gql_mutations import create_attachments
from claim.models import Claim

from api_fhir_r4.converters.containedResourceConverter import ContainedResourceConverter
from api_fhir_r4.mixins import ContainedContentSerializerMixin
from api_fhir_r4.models import Claim as FHIRClaim
from django.http import HttpResponseForbidden
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404

from api_fhir_r4.configurations import R4ClaimConfig
from api_fhir_r4.converters import ClaimResponseConverter, OperationOutcomeConverter, PatientConverter, \
    ConditionConverter, MedicationConverter, HealthcareServiceConverter, PractitionerConverter, \
    ActivityDefinitionConverter
from api_fhir_r4.converters.claimConverter import ClaimConverter
from api_fhir_r4.models import FHIRBaseObject
from api_fhir_r4.serializers import BaseFHIRSerializer


class ClaimSerializer(BaseFHIRSerializer, ContainedContentSerializerMixin):

    fhirConverter = ClaimConverter()

    contained_resources = [
        ContainedResourceConverter('insuree', PatientConverter),
        ContainedResourceConverter('icd', ConditionConverter),
        *[ContainedResourceConverter('icd_{}'.format(n), ConditionConverter) for n in range(1, 5)],
        ContainedResourceConverter('health_facility', HealthcareServiceConverter),
        ContainedResourceConverter('admin', PractitionerConverter),
        ContainedResourceConverter('items', MedicationConverter,
                                   lambda model, field: [
                                       item.item for item in model.__getattribute__(field).all()
                                   ]),
        ContainedResourceConverter('services', ActivityDefinitionConverter,
                                   lambda model, field: [
                                       service.service for service in model.__getattribute__(field).all()
                                   ]),
    ]

    def create(self, validated_data):
        claim_submit = ClaimSubmit(date=validated_data.get('date_claimed'),
                                   code=validated_data.get('code'),
                                   icd_code=validated_data.get('icd_code'),
                                   icd_code_1=validated_data.get('icd1_code'),
                                   icd_code_2=validated_data.get('icd2_code'),
                                   icd_code_3=validated_data.get('icd3_code'),
                                   icd_code_4=validated_data.get('icd4_code'),
                                   total=validated_data.get('claimed'),
                                   start_date=validated_data.get('date_from'),
                                   end_date=validated_data.get('date_to'),
                                   insuree_chf_id=validated_data.get('insuree_chf_code'),
                                   health_facility_code=validated_data.get('health_facility_code'),
                                   claim_admin_code=validated_data.get('claim_admin_code'),
                                   visit_type=validated_data.get('visit_type'),
                                   guarantee_no=validated_data.get('guarantee_id'),
                                   item_submits=validated_data.get('submit_items'),
                                   service_submits=validated_data.get('submit_services'),
                                   comment=validated_data.get('explanation'),
                                   )
        request = self.context.get("request")
        if request.user and request.user.has_perms(ClaimConfig.gql_mutation_create_claims_perms):
            ClaimSubmitService(request.user).submit(claim_submit)
            self.create_claim_attachments(validated_data.get('code'),
                                          attachments=validated_data.get('claim_attachments', []))
            return self.create_claim_response(validated_data.get('code'))
        else:
            return HttpResponseForbidden()

    def create_claim_response(self, claim_code):
        claim = get_object_or_404(Claim, code=claim_code)
        return ClaimResponseConverter.to_fhir_obj(claim)

    def create_claim_attachments(self, claim_code, attachments):
        claim = get_object_or_404(Claim, code=claim_code)
        create_attachments(claim.id, attachments)

    def to_representation(self, obj):
        if isinstance(obj, HttpResponseBase):
            return OperationOutcomeConverter.to_fhir_obj(obj).toDict()
        elif isinstance(obj, FHIRBaseObject):
            return obj.toDict()

        fhir_obj = self.fhirConverter.to_fhir_obj(obj)
        self.remove_attachment_data(fhir_obj)

        fhir_dict = fhir_obj.toDict()
        if self.context.get('contained', False):
            fhir_dict['contained'] = self._create_contained_obj_dict(obj)
        return fhir_dict

    def remove_attachment_data(self, fhir_obj):
        if hasattr(self.parent, 'many') and self.parent.many is True:
            attachments = self.__get_attachments(fhir_obj)
            for next_attachment in attachments:
                next_attachment.data = None

    def __get_attachments(self, fhir_obj):
        attachment_category = R4ClaimConfig.get_fhir_claim_attachment_code()
        return [a.valueAttachment for a in fhir_obj.supportingInfo if a.category.text == attachment_category]

    # def _add_contained_resources(self, imis_obj: Claim, fhir_obj: FHIRClaim):
    #     for attribute, converter in self.contained_resources.items():
    #         attr_value = imis_obj.__getattribute__(attribute)
    #         if attr_value is not None:
    #             try:
    #                 fhir_value = converter().to_fhir_obj(attr_value)
    #                 print("Attr: {} Attr val: {}".format(attribute, fhir_value))
    #             except Exception as e:
    #                 print("FAILED TO PROCESS: {}".format((attribute, attr_value)))
    #     # Added resources: Patient, Condition, Medication, HealthcareService, Practitioner, ActivityDefinition.
    #     pass
    #
    # # def __get_related_field_value(self, imis_obj, attribute):
    # #     attr_value = imis_obj.__getattribute__(attribute)
    # #     if isinstance(attr_value, MyModel.my_relation.__class__)