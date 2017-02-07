from openprocurement.tender.openeu.views.qualification import TenderQualificationResource as BaseTenderQualificationResource
from openprocurement.tender.openeu.utils import qualifications_resource


@qualifications_resource(
    name='Tender newOpenEU Qualification',
    collection_path='/tenders/{tender_id}/qualifications',
    path='/tenders/{tender_id}/qualifications/{qualification_id}',
    procurementMethodType='newOpenEU',
    description="Tender newOpenEU Qualification")
class TenderQualificationResource(BaseTenderQualificationResource):
    pass
