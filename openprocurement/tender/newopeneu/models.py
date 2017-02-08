from datetime import timedelta
from schematics.exceptions import ValidationError
from schematics.types.serializable import serializable
from schematics.types.compound import ModelType
from schematics.types import BooleanType

from openprocurement.tender.openeu.models import Tender as OpenEUTender, EnquiryPeriod, ENQUIRY_STAND_STILL_TIME, \
                                                 Bid as BaseBid
from schematics.types import StringType
from openprocurement.tender.newopeneu.constants import TENDERING_DAYS, TENDERING_DURATION, QUESTIONS_STAND_STILL, \
    COMPLAINT_SUBMIT_TIME
from openprocurement.tender.openua.utils import calculate_business_date
from openprocurement.api.models import get_now, Period
from openprocurement.tender.openeu.models import SifterListType, BidModelType


class Bid(BaseBid):
    selfQualified = BooleanType()
    selfEligible = BooleanType()
    eligibilityDocuments = None
    qualificationDocuments = None


class Tender(OpenEUTender):
    procurementMethodType = StringType(default="newOpenEU")
    bids = SifterListType(BidModelType(Bid), default=list(), filter_by='status',
                          filter_in_values=['invalid', 'invalid.pre-qualification', 'deleted'])

    def validate_tenderPeriod(self, data, period):
        # if data['_rev'] is None when tender was created just now
        if not data['_rev'] and calculate_business_date(get_now(), -timedelta(minutes=10)) >= period.startDate:
            raise ValidationError(u"tenderPeriod.startDate should be in greater than current date")
        if period and calculate_business_date(period.startDate, TENDERING_DURATION, data) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than {} days".format(TENDERING_DAYS))

    def initialize(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, self)
        self.enquiryPeriod = EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                                endDate=endDate,
                                                invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                                                clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))
        now = get_now()
        self.date = now
        if self.lots:
            for lot in self.lots:
                lot.date = now

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, self)
        return EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                  endDate=endDate,
                                  invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                                  clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=calculate_business_date(self.tenderPeriod.startDate, COMPLAINT_SUBMIT_TIME, self)))

