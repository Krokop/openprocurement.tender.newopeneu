import os

from openprocurement.tender.openeu.tests import bid
from openprocurement.tender.newopeneu.tests.base import test_tender_data


relative_to = os.path.dirname(__file__)


class TenderBidResourceTest(bid.TenderBidResourceTest):
    relative_to = relative_to
    initial_data = test_tender_data


class TenderBidFeaturesResourceTest(bid.TenderBidFeaturesResourceTest):
    relative_to = relative_to
    initial_data = test_tender_data


class TenderBidDocumentResourceTest(bid.TenderBidDocumentResourceTest):
    relative_to = relative_to
    initial_data = test_tender_data


class TenderBidDocumentWithDSResourceTest(bid.TenderBidDocumentWithDSResourceTest):
    relative_to = relative_to
    initial_data = test_tender_data
