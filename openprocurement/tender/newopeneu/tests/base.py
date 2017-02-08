# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime, timedelta

from openprocurement.tender.openeu.tests.base import test_tender_data as base_test_tender_data, \
    test_features_tender_data as base_test_features_tender_data, test_bids as base_test_bids
from openprocurement.tender.newopeneu.constants import TENDERING_DAYS

now = datetime.now()
test_tender_data = deepcopy(base_test_tender_data)
test_tender_data["procurementMethodType"] = "newOpenEU"
test_tender_data["tenderPeriod"] = {"endDate": (now + timedelta(days=TENDERING_DAYS + 1)).isoformat()}
test_features_tender_data = deepcopy(base_test_features_tender_data)
test_features_tender_data["procurementMethodType"] = "newOpenEU"
test_features_tender_data["tenderPeriod"] = {"endDate": (now + timedelta(days=TENDERING_DAYS + 1)).isoformat()}
test_bids = deepcopy(base_test_bids)
test_bids[0]['selfQualified'] = None
test_bids[0]['selfEligible'] = None
test_bids[1]['selfQualified'] = None
test_bids[1]['selfEligible'] = None
