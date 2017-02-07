# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.contract import TenderAwardContractResource as BaseResource


@opresource(name='Tender newOpenEU Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType='newOpenEU',
            description="Tender newOpenEU contracts")
class TenderAwardContractResource(BaseResource):
    """ """
    pass
