# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.award import TenderAwardResource as BaseResource


@opresource(name='Tender newOpenEU Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender newOpenEU awards",
            procurementMethodType='newOpenEU')
class TenderAwardResource(BaseResource):
    """ EU award resource """
