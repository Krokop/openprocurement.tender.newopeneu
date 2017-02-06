from copy import deepcopy
from datetime import datetime, timedelta

from openprocurement.tender.openeu.tests.base import test_tender_data as base_test_tender_data

now = datetime.now()
test_tender_data = deepcopy(base_test_tender_data)
test_tender_data["procurementMethodType"] = "newOpenEU"
test_tender_data["tenderPeriod"] = {"endDate": (now + timedelta(days=TENDERING_DAYS + 1)).isoformat()}
