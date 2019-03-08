import unittest
from datetime import timedelta
from datetime import timezone
from unittest import TestCase

from dtc.compat import datetime


class TestDateTimeCompat(TestCase):
    def setUp(self):
        self.theclass = datetime

    def test_fromisoformat(self):
        # Test that isoformat() is reversible
        base_dates = [
            (1, 1, 1),
            (1000, 2, 14),
            (1900, 1, 1),
            (2000, 2, 29),
            (2004, 11, 12),
            (2004, 4, 3),
            (2017, 5, 30),
        ]

        for dt_tuple in base_dates:
            dt = self.theclass(*dt_tuple)
            dt_str = dt.isoformat()
            with self.subTest(dt_str=dt_str):
                dt_rt = self.theclass.fromisoformat(dt.isoformat())

                self.assertEqual(dt, dt_rt)

    def test_fromisoformat_subclass(self):
        class DateSubclass(self.theclass):
            pass

        dt = DateSubclass(2014, 12, 14)

        dt_rt = DateSubclass.fromisoformat(dt.isoformat())

        self.assertIsInstance(dt_rt, DateSubclass)

    def test_fromisoformat_fails(self):
        # Test that fromisoformat() fails on invalid values
        bad_strs = [
            "",  # Empty string
            "009-03-04",  # Not 10 characters
            "123456789",  # Not a date
            "200a-12-04",  # Invalid character in year
            "2009-1a-04",  # Invalid character in month
            "2009-12-0a",  # Invalid character in day
            "2009-01-32",  # Invalid day
            "2009-02-29",  # Invalid leap day
            "20090228",  # Valid ISO8601 output not from isoformat()
        ]

        for bad_str in bad_strs:
            with self.assertRaises(ValueError):
                self.theclass.fromisoformat(bad_str)

    def test_fromisoformat_fails_typeerror(self):
        # Test that fromisoformat fails when passed the wrong type
        import io

        bad_types = [b'2009-03-01', None, io.StringIO('2009-03-01')]
        for bad_type in bad_types:
            with self.assertRaises(TypeError):
                self.theclass.fromisoformat(bad_type)


    def test_isoformat_timezone(self):
        tzoffsets = [
            ("05:00", timedelta(hours=5)),
            ("02:00", timedelta(hours=2)),
            ("06:27", timedelta(hours=6, minutes=27)),

            # no seconds in timezone in ython  3.6
            # ("12:32:30", timedelta(hours=12, minutes=32, seconds=30)),
            # (
            #     "02:04:09.123456",
            #     timedelta(hours=2, minutes=4, seconds=9, microseconds=123456),
            # ),
        ]

        tzinfos = [
            ("", None),
            ("+00:00", timezone.utc),
            ("+00:00", timezone(timedelta(0))),
        ]

        tzinfos += [
            (prefix + expected, timezone(sign * td))
            for expected, td in tzoffsets
            for prefix, sign in [("-", -1), ("+", 1)]
        ]

        dt_base = self.theclass(2016, 4, 1, 12, 37, 9)
        exp_base = "2016-04-01T12:37:09"

        for exp_tz, tzi in tzinfos:
            dt = dt_base.replace(tzinfo=tzi)
            exp = exp_base + exp_tz
            with self.subTest(tzi=tzi):
                assert dt.isoformat() == exp

    def test_format(self):
        dt = self.theclass(2007, 9, 10, 4, 5, 1, 123)
        self.assertEqual(dt.__format__(''), str(dt))

    def test_fromisoformat_datetime(self):
        # Test that isoformat() is reversible
        base_dates = [(1, 1, 1), (1900, 1, 1), (2004, 11, 12), (2017, 5, 30)]

        base_times = [
            (0, 0, 0, 0),
            (0, 0, 0, 241000),
            (0, 0, 0, 234567),
            (12, 30, 45, 234567),
        ]

        separators = [" ", "T"]

        tzinfos = [
            None,
            timezone.utc,
            timezone(timedelta(hours=-5)),
            timezone(timedelta(hours=2)),
        ]

        dts = [
            self.theclass(*date_tuple, *time_tuple, tzinfo=tzi)
            for date_tuple in base_dates
            for time_tuple in base_times
            for tzi in tzinfos
        ]

        for dt in dts:
            for sep in separators:
                dtstr = dt.isoformat(sep=sep)

                with self.subTest(dtstr=dtstr):
                    dt_rt = self.theclass.fromisoformat(dtstr)
                    self.assertEqual(dt, dt_rt)

    def test_fromisoformat_timezone(self):
        base_dt = self.theclass(2014, 12, 30, 12, 30, 45, 217456)

        tzoffsets = [
            timedelta(hours=5),
            timedelta(hours=2),
            timedelta(hours=6, minutes=27),
            # timedelta(hours=12, minutes=32, seconds=30),
            # timedelta(hours=2, minutes=4, seconds=9, microseconds=123456),
        ]

        tzoffsets += [-1 * td for td in tzoffsets]

        tzinfos = [None, timezone.utc, timezone(timedelta(hours=0))]

        tzinfos += [timezone(td) for td in tzoffsets]

        for tzi in tzinfos:
            dt = base_dt.replace(tzinfo=tzi)
            dtstr = dt.isoformat()

            with self.subTest(tstr=dtstr):
                dt_rt = self.theclass.fromisoformat(dtstr)
                assert dt == dt_rt, dt_rt

    def test_fromisoformat_separators(self):
        separators = [
            " ",
            "T",
            "\u007f",  # 1-bit widths
            "\u0080",
            "ʁ",  # 2-bit widths
            "ᛇ",
            "時",  # 3-bit widths
            "🐍",  # 4-bit widths
        ]

        for sep in separators:
            dt = self.theclass(2018, 1, 31, 23, 59, 47, 124789)
            dtstr = dt.isoformat(sep=sep)

            with self.subTest(dtstr=dtstr):
                dt_rt = self.theclass.fromisoformat(dtstr)
                self.assertEqual(dt, dt_rt)

    def test_fromisoformat_ambiguous(self):
        # Test strings like 2018-01-31+12:15 (where +12:15 is not a time zone)
        separators = ["+", "-"]
        for sep in separators:
            dt = self.theclass(2018, 1, 31, 12, 15)
            dtstr = dt.isoformat(sep=sep)

            with self.subTest(dtstr=dtstr):
                dt_rt = self.theclass.fromisoformat(dtstr)
                self.assertEqual(dt, dt_rt)

    def test_fromisoformat_timespecs(self):
        datetime_bases = [(2009, 12, 4, 8, 17, 45, 123456), (2009, 12, 4, 8, 17, 45, 0)]

        tzinfos = [
            None,
            timezone.utc,
            timezone(timedelta(hours=-5)),
            timezone(timedelta(hours=2)),
            timezone(timedelta(hours=6, minutes=27)),
        ]

        timespecs = ["hours", "minutes", "seconds", "milliseconds", "microseconds"]

        for ip, ts in enumerate(timespecs):
            for tzi in tzinfos:
                for dt_tuple in datetime_bases:
                    if ts == "milliseconds":
                        new_microseconds = 1000 * (dt_tuple[6] // 1000)
                        dt_tuple = dt_tuple[0:6] + (new_microseconds,)

                    dt = self.theclass(*(dt_tuple[0 : (4 + ip)]), tzinfo=tzi)
                    dtstr = dt.isoformat(timespec=ts)
                    with self.subTest(dtstr=dtstr):
                        dt_rt = self.theclass.fromisoformat(dtstr)
                        self.assertEqual(dt, dt_rt)

    def test_fromisoformat_fails_datetime(self):
        # Test that fromisoformat() fails on invalid values
        bad_strs = [
            "",  # Empty string
            "2009.04-19T03",  # Wrong first separator
            "2009-04.19T03",  # Wrong second separator
            "2009-04-19T0a",  # Invalid hours
            "2009-04-19T03:1a:45",  # Invalid minutes
            "2009-04-19T03:15:4a",  # Invalid seconds
            "2009-04-19T03;15:45",  # Bad first time separator
            "2009-04-19T03:15;45",  # Bad second time separator
            "2009-04-19T03:15:4500:00",  # Bad time zone separator
            "2009-04-19T03:15:45.2345",  # Too many digits for milliseconds
            "2009-04-19T03:15:45.1234567",  # Too many digits for microseconds
            "2009-04-19T03:15:45.123456+24:30",  # Invalid time zone offset
            "2009-04-19T03:15:45.123456-24:30",  # Invalid negative offset
            "2009-04-10ᛇᛇᛇᛇᛇ12:15",  # Too many unicode separators
            "2009-04-19T1",  # Incomplete hours
            "2009-04-19T12:3",  # Incomplete minutes
            "2009-04-19T12:30:4",  # Incomplete seconds
            "2009-04-19T12:",  # Ends with time separator
            "2009-04-19T12:30:",  # Ends with time separator
            "2009-04-19T12:30:45.",  # Ends with time separator
            "2009-04-19T12:30:45.123456+",  # Ends with timzone separator
            "2009-04-19T12:30:45.123456-",  # Ends with timzone separator
            "2009-04-19T12:30:45.123456-05:00a",  # Extra text
            "2009-04-19T12:30:45.123-05:00a",  # Extra text
            "2009-04-19T12:30:45-05:00a",  # Extra text
        ]

        for bad_str in bad_strs:
            with self.subTest(bad_str=bad_str):
                with self.assertRaises(ValueError):
                    self.theclass.fromisoformat(bad_str)

    def test_fromisoformat_utc(self):
        dt_str = "2014-04-19T13:21:13+00:00"
        dt = self.theclass.fromisoformat(dt_str)

        self.assertIs(dt.tzinfo, timezone.utc)

    def test_fromisoformat_subclass2(self):
        class DateTimeSubclass(self.theclass):
            pass

        dt = DateTimeSubclass(
            2014,
            12,
            14,
            9,
            30,
            45,
            457390,
            tzinfo=timezone(timedelta(hours=10, minutes=45)),
        )

        dt_rt = DateTimeSubclass.fromisoformat(dt.isoformat())

        self.assertEqual(dt, dt_rt)
        self.assertIsInstance(dt_rt, DateTimeSubclass)


if __name__ == "__main__":
    unittest.main()
