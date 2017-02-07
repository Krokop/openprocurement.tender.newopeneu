# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.auction import TenderAuctionResource as BaseResource


@opresource(name='Tender newOpenEU Auction',
            collection_path='/tenders/{tender_id}/auction',
            path='/tenders/{tender_id}/auction/{auction_lot_id}',
            procurementMethodType='newOpenEU',
            description="Tender newOpenEU auction data")
class TenderAuctionResource(BaseResource):
    """ Auctions resouce """
    pass
