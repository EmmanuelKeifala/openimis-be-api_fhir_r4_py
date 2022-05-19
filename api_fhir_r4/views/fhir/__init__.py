from api_fhir_r4.views.fhir.activity_definition import ActivityDefinitionViewSet
from api_fhir_r4.views.fhir.claim import ClaimViewSet
from api_fhir_r4.views.fhir.claim_response import ClaimResponseViewSet
from api_fhir_r4.views.fhir.code_systems.diagnosis import CodeSystemOpenIMISDiagnosisViewSet
from api_fhir_r4.views.fhir.code_systems.group_confirmation_type import CodeSystemOpenIMISGroupConfirmationTypeViewSet
from api_fhir_r4.views.fhir.code_systems.group_type import CodeSystemOpenIMISGroupTypeViewSet
from api_fhir_r4.views.fhir.code_systems.organization_hf_legal_form import CodeSystemOrganizationHFLegalFormViewSet
from api_fhir_r4.views.fhir.code_systems.organization_hf_level import CodeSystemOrganizationHFLevelViewSet
from api_fhir_r4.views.fhir.code_systems.organization_ph_activity import CodeSystemOrganizationPHActivityViewSet
from api_fhir_r4.views.fhir.code_systems.organization_ph_legal_form import CodeSystemOrganizationPHLegalFormViewSet
from api_fhir_r4.views.fhir.code_systems.patient_education_level import CodeSystemOpenIMISPatientEducationLevelViewSet
from api_fhir_r4.views.fhir.code_systems.patient_identification_type import \
    CodeSystemOpenIMISPatientIdentificationTypeViewSet
from api_fhir_r4.views.fhir.code_systems.patient_profession import CodeSystemOpenIMISPatientProfessionViewSet
from api_fhir_r4.views.fhir.code_systems.patient_relationship import CodeSystemOpenIMISPatientRelationshipViewSet
from api_fhir_r4.views.fhir.communication import CommunicationViewSet
from api_fhir_r4.views.fhir.communication_request import CommunicationRequestViewSet
from api_fhir_r4.views.fhir.contract import ContractViewSet
from api_fhir_r4.views.fhir.coverage_eligibility_request import CoverageEligibilityRequestViewSet
from api_fhir_r4.views.fhir.coverage_request import CoverageRequestQuerySet
from api_fhir_r4.views.fhir.group import GroupViewSet
from api_fhir_r4.views.fhir.insurance_plan import ProductViewSet
from api_fhir_r4.views.fhir.insuree import InsureeViewSet
from api_fhir_r4.views.fhir.invoice import InvoiceViewSet
from api_fhir_r4.views.fhir.location import LocationViewSet
from api_fhir_r4.views.fhir.medication import MedicationViewSet
from api_fhir_r4.views.fhir.organisation import OrganisationViewSet
from api_fhir_r4.views.fhir.practitioner import PractitionerViewSet
from api_fhir_r4.views.fhir.practitioner_role import PractitionerRoleViewSet
from api_fhir_r4.views.fhir.subscription import SubscriptionViewSet
