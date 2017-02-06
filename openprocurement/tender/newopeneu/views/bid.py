from openprocurement.tender.openeu.views.bid import TenderBidResource as BaseResource
from openprocurement.api.utils import opresource


@opresource(name='Tender newOpenEU Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType='newOpenEU',
            description="Tender newOpenEU bids")
class TenderBidResource(BaseResource):
    pass
