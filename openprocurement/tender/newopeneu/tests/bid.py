import os

from openprocurement.tender.openeu.tests import bid
from openprocurement.tender.newopeneu.tests.base import test_tender_data, test_features_tender_data
from openprocurement.tender.openeu.tests.base import test_bids


relative_to = os.path.dirname(__file__)


class TenderBidResourceTest(bid.TenderBidResourceTest):
    relative_to = relative_to
    initial_data = test_tender_data

    def test_bids_invalidation_on_tender_change(self):
        bids_access = {}

        # submit bids
        for data in test_bids:
            response = self.app.post_json('/tenders/{}/bids'.format(
                self.tender_id), {'data': data})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            bids_access[response.json['data']['id']] = response.json['access']['token']

        # check initial status
        for bid_id, token in bids_access.items():
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'pending')

        # update tender. we can set value that is less than a value in bids as
        # they will be invalidated by this request
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data":
                {"value": {'amount': 300.0}}
        })
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["value"]["amount"], 300)

        # check bids status
        for bid_id, token in bids_access.items():
            response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid_id, token))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'invalid')
        # try to add documents to bid
        for doc_resource in ['documents', 'financial_documents']:
            response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
                self.tender_id, bid_id, doc_resource, token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')], status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['errors'][0]["description"], "Can't add document to 'invalid' bid")

        # check that tender status change does not invalidate bids
        # submit one more bid. check for invalid value first
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bids[0]}, status=422)
        self.assertEqual(response.status, '422 Unprocessable Entity')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': [u'value of bid should be less than value of tender'], u'location': u'body', u'name': u'value'}
        ])
        # and submit valid bid
        data = test_bids[0]
        data['value']['amount'] = 299
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': data})
        self.assertEqual(response.status, '201 Created')
        valid_bid_id = response.json['data']['id']
        valid_bid_token = response.json['access']['token']
        valid_bid_date = response.json['data']['date']

        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[1]['tenderers'], "value": {"amount": 101}}})

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(
            self.tender_id, qualification['id']), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, valid_bid_id, valid_bid_token))
        self.assertEqual(response.json['data']['status'], 'active')

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        # switch to qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                      {'data': {'bids': auction_bids_data}})
        self.assertEqual(response.status, "200 OK")
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.qualification")
        # tender should display all bids
        self.assertEqual(len(response.json['data']['bids']), 4)
        self.assertEqual(response.json['data']['bids'][2]['date'], valid_bid_date)
        # invalidated bids should show only 'id' and 'status' fields
        for bid in response.json['data']['bids']:
            if bid['status'] == 'invalid':
                self.assertTrue('id' in bid)
                self.assertFalse('value' in bid)
                self.assertFalse('tenderers' in bid)
                self.assertFalse('date' in bid)

        # invalidated bids stay invalidated
        for bid_id, token in bids_access.items():
            response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, bid_id))
            self.assertEqual(response.status, '200 OK')
            self.assertEqual(response.json['data']['status'], 'invalid')
            # invalidated bids displays only 'id' and 'status' fields
            self.assertFalse('value' in response.json['data'])
            self.assertFalse('tenderers' in response.json['data'])
            self.assertFalse('date' in response.json['data'])

        # and valid bid is not invalidated
        response = self.app.get('/tenders/{}/bids/{}'.format(self.tender_id, valid_bid_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'active')
        # and displays all his data
        self.assertTrue('value' in response.json['data'])
        self.assertTrue('tenderers' in response.json['data'])
        self.assertTrue('date' in response.json['data'])

        # check bids availability on finished tender
        self.set_status('complete')
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json['data']['bids']), 4)
        for bid in response.json['data']['bids']:
            if bid['id'] in bids_access:  # previously invalidated bids
                self.assertEqual(bid['status'], 'invalid')
                self.assertFalse('value' in bid)
                self.assertFalse('tenderers' in bid)
                self.assertFalse('date' in bid)
            else:  # valid bid
                self.assertEqual(bid['status'], 'active')
                self.assertTrue('value' in bid)
                self.assertTrue('tenderers' in bid)
                self.assertTrue('date' in bid)

    def test_delete_tender_bidder(self):
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 500}}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid = response.json['data']
        bid_token = response.json['access']['token']

        response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['id'], bid['id'])
        self.assertEqual(response.json['data']['status'], 'deleted')
        # deleted bid does not contain bid information
        self.assertFalse('value' in response.json['data'])
        self.assertFalse('tenderers' in response.json['data'])
        self.assertFalse('date' in response.json['data'])

        # try to add documents to bid
        for doc_resource in ['documents', 'financial_documents']:
            response = self.app.post('/tenders/{}/bids/{}/{}?acc_token={}'.format(
                self.tender_id, bid['id'], doc_resource, bid_token), upload_files=[('file', 'name_{}.doc'.format(doc_resource[:-1]), 'content')], status=403)
            self.assertEqual(response.status, '403 Forbidden')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['errors'][0]["description"], "Can't add document to 'deleted' bid")

        revisions = self.db.get(self.tender_id).get('revisions')
        self.assertTrue(any([i for i in revisions[-2][u'changes'] if i['op'] == u'remove' and i['path'] == u'/bids']))
        self.assertTrue(any([i for i in revisions[-1][u'changes'] if i['op'] == u'replace' and i['path'] == u'/bids/0/status']))

        response = self.app.delete('/tenders/{}/bids/some_id'.format(self.tender_id), status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'bid_id'}
        ])

        response = self.app.delete('/tenders/some_id/bids/some_id', status=404)
        self.assertEqual(response.status, '404 Not Found')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'error')
        self.assertEqual(response.json['errors'], [
            {u'description': u'Not Found', u'location':
                u'url', u'name': u'tender_id'}
        ])

        # create new bid
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 500}}})
        self.assertEqual(response.status, '201 Created')
        bid = response.json['data']
        bid_token = response.json['access']['token']

        # update tender. we can set value that is less than a value in bid as
        # they will be invalidated by this request
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data":
                {"value": {'amount': 300.0}}
        })
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']["value"]["amount"], 300)

        # check bid 'invalid' status
        response = self.app.get('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data']['status'], 'invalid')

        # try to delete 'invalid' bid
        response = self.app.delete('/tenders/{}/bids/{}?acc_token={}'.format(self.tender_id, bid['id'], bid_token))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['id'], bid['id'])
        self.assertEqual(response.json['data']['status'], 'deleted')

        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[0]['tenderers'], "value": {"amount": 100}}})
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': test_bids[1]['tenderers'], "value": {"amount": 101}}})

        # switch to active.pre-qualification
        self.set_status('active.pre-qualification', {"id": self.tender_id, 'status': 'active.tendering'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification')

        # qualify bids
        response = self.app.get('/tenders/{}/qualifications'.format(self.tender_id))
        self.app.authorization = ('Basic', ('token', ''))
        for qualification in response.json['data']:
            response = self.app.patch_json('/tenders/{}/qualifications/{}'.format(
            self.tender_id, qualification['id']), {"data": {"status": "active", "qualified": True, "eligible": True}})
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {"status": 'active.pre-qualification.stand-still'}})
        self.assertEqual(response.json['data']['status'], 'active.pre-qualification.stand-still')

        # switch to active.auction
        self.set_status('active.auction', {"id": self.tender_id, 'status': 'active.pre-qualification.stand-still'})
        self.app.authorization = ('Basic', ('chronograph', ''))
        response = self.app.patch_json('/tenders/{}'.format(
            self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.json['data']['status'], "active.auction")

        # switch to qualification
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(self.tender_id))
        auction_bids_data = response.json['data']['bids']
        response = self.app.post_json('/tenders/{}/auction'.format(self.tender_id),
                                      {'data': {'bids': auction_bids_data}})
        self.assertEqual(response.status, "200 OK")
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.qualification")

        # get awards
        response = self.app.get('/tenders/{}/awards'.format(self.tender_id))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending'][0]

        self.app.authorization = ('Basic', ('token', ''))
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, award_id, self.tender_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
        self.assertEqual(response.status, "200 OK")
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], "active.awarded")

        # time travel
        tender = self.db.get(self.tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)

        # sign contract
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        self.app.authorization = ('Basic', ('token', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(
            self.tender_id, contract_id, self.tender_token), {"data": {"status": "active"}})
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.json['data']['status'], 'complete')

        # finished tender does not show deleted bid info
        response = self.app.get('/tenders/{}'.format(self.tender_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['data']['bids']), 4)
        bid_data = response.json['data']['bids'][1]
        self.assertEqual(bid_data['id'], bid['id'])
        self.assertEqual(bid_data['status'], 'deleted')
        self.assertFalse('value' in bid_data)
        self.assertFalse('tenderers' in bid_data)
        self.assertFalse('date' in bid_data)


class TenderBidFeaturesResourceTest(bid.TenderBidFeaturesResourceTest):
    relative_to = relative_to
    initial_data = test_features_tender_data


