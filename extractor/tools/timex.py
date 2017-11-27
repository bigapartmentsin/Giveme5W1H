import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Timex:
    _date_format_month = '%Y-%m'
    _date_format_week = '%Y-W%W' + '-%w'
    _date_format_day = '%Y-%m-%d'
    _date_format_time_nosecs = '%Y-%m-%dT%H:%M'
    _log = logging.getLogger('GiveMe5W')

    def __init__(self, start_datetime, end_datetime):
        self._start_date = start_datetime
        self._end_date = end_datetime

    def __str__(self):
        return 'Timex(' + str(self._start_date) + ', ' + str(self._end_date) + ')'

    def get_start_date(self):
        return self._start_date

    def get_end_date(self):
        return self._end_date

    def get_duration(self):
        return self._end_date - self._start_date

    def is_entailed_in(self, other_timex):
        return other_timex.get_start_date() <= self._start_date and self.get_end_date() <= other_timex._end_date

    def get_json(self):
        """
        return a serializable representation of this object.
        Representation miming the timex3(xml) standard,
        but limited to ranges based on two dates without any quant or freq information

        http://www.timeml.org/publications/timeMLdocs/timeml_1.2.1.html#timex3
        <TIMEX3 tid="t1" type="DATE" value="1992">
        <TIMEX3 tid="t2" type="DATE" value="2000" mod="START">the dawn of 2000</TIMEX3>
        <TIMEX3 tid="t3" type="DURATION" beginPoint="t1" endPoint="t2"></TIMEX3>
        :return:
        """
        return [
            {
                'tid': 't1',
                'type': 'DATE',
                'value': self._start_date.isoformat()
            },
            {
                'tid': 't2',
                'type': 'DATE',
                'value': self._end_date.isoformat()
            },
            {
                'tid': 't3',
                'type': 'DURATION',
                'beginPoint': 't1',
                'endPoint': 't2'
            }
        ]


    @staticmethod
    def from_timex_text(text):
        # month (2017-11)
        try:
            start_date = datetime.strptime(text, Timex._date_format_month)
            end_date = start_date + relativedelta(months=1) - relativedelta(seconds=1)
            return Timex(start_date, end_date)
        except ValueError as verr:
            pass

        # week (2017-W45)
        try:
            default_day = '-0'  # https://stackoverflow.com/a/17087427/1455800
            start_date = datetime.strptime(text + default_day, Timex._date_format_week)
            end_date = start_date + relativedelta(weeks=1) - relativedelta(seconds=1)
            return Timex(start_date, end_date)
        except ValueError as verr:
            pass

        # day (2017-11-01)
        try:
            start_date = datetime.strptime(text, Timex._date_format_day)
            end_date = start_date + relativedelta(days=1) - relativedelta(seconds=1)
            return Timex(start_date, end_date)
        except ValueError as verr:
            pass

        # datetime without seconds (2017-02-04T13:55)
        try:
            start_date = datetime.strptime(text, Timex._date_format_time_nosecs)
            end_date = start_date + relativedelta(minutes=1) - relativedelta(seconds=1)
            return Timex(start_date, end_date)
        except ValueError as verr:
            pass

        #Timex._log.error('could not parse "' + text + '" to Timex')
        #print('could not parse "' + text + '" to Timex')
        # we cannot parse the following things
        #could not parse "2017-SU" to Timex: This summer
        return None
