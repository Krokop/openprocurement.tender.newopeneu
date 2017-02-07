# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.bid_document import TenderEUBidDocumentResource
from openprocurement.tender.openeu.utils import (
    bid_financial_documents_resource, bid_eligibility_documents_resource,
    bid_qualification_documents_resource)


@opresource(name='Tender newOpenEU Bid Documents',
            collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
            path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
            procurementMethodType='newOpenEU',
            description="Tender newOpenEU bidder documents")
class TendernewOpenEUBidDocumentResource(TenderEUBidDocumentResource):
    pass


@bid_financial_documents_resource(
    name='Tender newOpenEU Bid Financial Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/financial_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}',
    procurementMethodType='newOpenEU',
    description="Tender newOpenEU bidder financial documents")
class TendernewOpenEUBidFinancialDocumentResource(TendernewOpenEUBidDocumentResource):
    """ Tender newOpenEU Bid Financial Documents """
    pass
