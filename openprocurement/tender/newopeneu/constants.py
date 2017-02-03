from datetime import timedelta

TENDERING_DAYS = 3
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
QUESTIONS_STAND_STILL = timedelta(days=1)
COMPLAINT_STAND_STILL = timedelta(seconds=1)
PREQUALIFICATION_COMPLAINT_STAND_STILL = timedelta(seconds=1)
COMPLAINT_SUBMIT_TIME = timedelta(seconds=1)