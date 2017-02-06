# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.views.question import TenderQuestionResource as BaseResource
from openprocurement.api.utils import opresource


@opresource(name='Tender newOpenEU Questions',
            collection_path='/tenders/{tender_id}/questions',
            path='/tenders/{tender_id}/questions/{question_id}',
            procurementMethodType='newOpenEU',
            description="Tender questions")
class TenderQuestionResource(BaseResource):
    """ TenderNewOpenEU Questions """
