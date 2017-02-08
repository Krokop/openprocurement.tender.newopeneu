# -*- coding: utf-8 -*-
import os
import unittest
import iso8601
from datetime import timedelta, datetime
from openprocurement.tender.newopeneu.models import Tender
from openprocurement.tender.newopeneu.tests.base import test_tender_data
from openprocurement.tender.openeu.tests import tender
from openprocurement.api.models import get_now, SANDBOX_MODE

relative_to = os.path.dirname(__file__)


class TenderTest(tender.TenderTest):

    initial_auth = ('Basic', ('broker', ''))

    def test_simple_add_tender(self):
        u = Tender(test_tender_data)
        u.tenderID = "UA-X"

        assert u.id is None
        assert u.rev is None

        u.store(self.db)

        assert u.id is not None
        assert u.rev is not None

        fromdb = self.db.get(u.id)

        assert u.tenderID == fromdb['tenderID']
        assert u.doc_type == "Tender"
        assert u.procurementMethodType == "newOpenEU"
        assert fromdb['procurementMethodType'] == "newOpenEU"

        u.delete_instance(self.db)


class TenderResourceTest(tender.TenderResourceTest):
    initial_auth = ('Basic', ('broker', ''))
    relative_to = relative_to
    initial_data = test_tender_data

    def test_tender_period_duration(self):
        request_path = '/tenders'

        # make request with tenderPeriod duration 2 days
        data = test_tender_data['tenderPeriod']
        test_tender_data['tenderPeriod'] = {'startDate': get_now().isoformat(),
                                            'endDate': (get_now() + timedelta(days=2)) .isoformat()}
        response = self.app.post_json(request_path, {'data': test_tender_data}, status=422)
        test_tender_data['tenderPeriod'] = data
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'][0]['description'][0], 'tenderPeriod should be greater than 3 days')

    def test_enquiry_period_duration(self):
        request_path = '/tenders'
        response = self.app.post_json(request_path, {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        tenderPeriod_endDate = iso8601.parse_date(response.json['data']['tenderPeriod']['endDate'])
        self.assertEqual(response.json['data']['enquiryPeriod']['endDate'], (tenderPeriod_endDate - timedelta(days=1)).isoformat())

    def test_complaint_period_duration(self):
        request_path = '/tenders'
        response = self.app.post_json(request_path, {'data': test_tender_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        complaintPeriod_startDate = iso8601.parse_date(response.json['data']['complaintPeriod']['startDate'])
        self.assertEqual(response.json['data']['complaintPeriod']['endDate'], (complaintPeriod_startDate + timedelta(seconds=1)).isoformat())


class TenderProcessTest(tender.TenderProcessTest):
    initial_auth = ('Basic', ('broker', ''))
    relative_to = relative_to
    initial_data = test_tender_data


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderProcessTest))
    suite.addTest(unittest.makeSuite(TenderResourceTest))
    suite.addTest(unittest.makeSuite(TenderTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
