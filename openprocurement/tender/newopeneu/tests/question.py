import os

from openprocurement.tender.newopeneu.tests.base import test_tender_data
from openprocurement.tender.openeu.tests import question
from openprocurement.tender.openeu.tests.base import test_bids


relative_to = os.path.dirname(__file__)


class TenderQuestionResourceTest(question.TenderQuestionResourceTest):
    initial_auth = ('Basic', ('broker', ''))
    relative_to = relative_to
    initial_data = test_tender_data


class TenderLotQuestionResourceTest(question.TenderLotQuestionResourceTest):
    initial_auth = ('Basic', ('broker', ''))
    relative_to = relative_to
    initial_data = test_tender_data

    def test_create_tender_question(self):
        None

    def test_patch_tender_question(self):
        None

    def test_lot_tender_question(self):
        response = self.app.post_json('/tenders/{}/questions'.format(self.tender_id), {'data': {
            'title': 'question title',
            'description': 'question description',
            "questionOf": "lot",
            "relatedItem": self.initial_lots[1]['id'],
            'author': test_bids[0]['tenderers'][0]
        }})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        question = response.json['data']

        response = self.app.patch_json('/tenders/{}/questions/{}?acc_token={}'.format(self.tender_id, question['id'], self.tender_token), {"data": {"answer": "answer"}})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")

        response = self.app.get('/tenders/{}/questions/{}'.format(self.tender_id, question['id']))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']["answer"], "answer")