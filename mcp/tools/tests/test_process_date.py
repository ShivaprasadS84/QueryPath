import unittest
import datetime
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetimetool.process_date import (
    get_current_date,
    get_date_with_offset,
    get_day_of_week,
    get_date_of_weekday,
    get_start_of_period,
    get_end_of_period,
    get_date_range_for_week,
    get_date_range_for_quarter
)


class TestProcessDateAtomic(unittest.TestCase):

    @patch('datetimetool.process_date.datetime')
    def test_get_current_date(self, mock_datetime):
        """Test get_current_date function"""
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        
        result = get_current_date()
        self.assertEqual(result, "18-07-2025")

    @patch('datetimetool.process_date.relativedelta')
    @patch('datetimetool.process_date.datetime')
    def test_get_date_with_offset_days(self, mock_datetime, mock_relativedelta):
        """Test get_date_with_offset function with days"""
        from dateutil.relativedelta import relativedelta
        
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        
        mock_base_date = datetime.date(2025, 1, 1)
        mock_datetime.datetime.strptime.return_value.date.return_value = mock_base_date
        
        mock_relativedelta.side_effect = lambda **kwargs: relativedelta(**kwargs)
        
        result = get_date_with_offset(5, 'days')
        self.assertEqual(result, "23-07-2025")
        
        result = get_date_with_offset(-3, 'days')
        self.assertEqual(result, "15-07-2025")
        
        result = get_date_with_offset(10, 'days', base_date_str="01-01-2025")
        self.assertEqual(result, "11-01-2025")

    @patch('datetimetool.process_date.relativedelta')
    @patch('datetimetool.process_date.datetime')
    def test_get_date_with_offset_weeks(self, mock_datetime, mock_relativedelta):
        """Test get_date_with_offset function with weeks"""
        from dateutil.relativedelta import relativedelta
        
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        mock_relativedelta.side_effect = lambda **kwargs: relativedelta(**kwargs)
        
        result = get_date_with_offset(2, 'weeks')
        self.assertEqual(result, "01-08-2025")
        
        result = get_date_with_offset(-1, 'weeks')
        self.assertEqual(result, "11-07-2025")

    @patch('datetimetool.process_date.relativedelta')
    @patch('datetimetool.process_date.datetime')
    def test_get_date_with_offset_months(self, mock_datetime, mock_relativedelta):
        """Test get_date_with_offset function with months"""
        from dateutil.relativedelta import relativedelta
        
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        mock_relativedelta.side_effect = lambda **kwargs: relativedelta(**kwargs)
        
        result = get_date_with_offset(3, 'months')
        self.assertEqual(result, "18-10-2025")
        
        result = get_date_with_offset(-6, 'months')
        self.assertEqual(result, "18-01-2025")

    @patch('datetimetool.process_date.relativedelta')
    @patch('datetimetool.process_date.datetime')
    def test_get_date_with_offset_years(self, mock_datetime, mock_relativedelta):
        """Test get_date_with_offset function with years"""
        from dateutil.relativedelta import relativedelta
        
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        mock_relativedelta.side_effect = lambda **kwargs: relativedelta(**kwargs)
        
        result = get_date_with_offset(1, 'years')
        self.assertEqual(result, "18-07-2026")
        
        result = get_date_with_offset(-2, 'years')
        self.assertEqual(result, "18-07-2023")

    def test_get_date_with_offset_invalid_unit(self):
        """Test get_date_with_offset function with invalid unit"""
        result = get_date_with_offset(5, 'invalid')
        self.assertIn("Invalid unit", result)

    def test_get_date_with_offset_invalid_date_format(self):
        """Test get_date_with_offset function with invalid date format"""
        result = get_date_with_offset(5, 'days', base_date_str="2025-07-18")
        self.assertIn("Invalid base_date_str format", result)

    @patch('datetimetool.process_date.datetime')
    def test_get_day_of_week(self, mock_datetime):
        """Test get_day_of_week function"""
        mock_today = datetime.date(2025, 7, 18)  # Friday
        mock_datetime.date.today.return_value = mock_today
        
        result = get_day_of_week()
        self.assertEqual(result, "Friday")
        
        mock_specific = datetime.date(2025, 12, 25)  # Thursday
        mock_datetime.datetime.strptime.return_value.date.return_value = mock_specific
        result = get_day_of_week("25-12-2025")
        self.assertEqual(result, "Thursday")

    def test_get_day_of_week_invalid_format(self):
        """Test get_day_of_week function with invalid date format"""
        result = get_day_of_week("2025-07-18")
        self.assertIn("Invalid date format", result)

    @patch('datetimetool.process_date.datetime')
    def test_get_date_of_weekday(self, mock_datetime):
        """Test get_date_of_weekday function"""
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.datetime.strptime.return_value.date.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_date_of_weekday('Monday', 'next')
        self.assertEqual(result, "21-07-2025")
        
        result = get_date_of_weekday('Wednesday', 'last')
        self.assertEqual(result, "16-07-2025")

    def test_get_date_of_weekday_invalid_weekday(self):
        """Test get_date_of_weekday function with invalid weekday"""
        result = get_date_of_weekday('InvalidDay', 'next')
        self.assertIn("Invalid weekday_name", result)

    def test_get_date_of_weekday_invalid_direction(self):
        """Test get_date_of_weekday function with invalid direction"""
        result = get_date_of_weekday('Monday', 'invalid')
        self.assertIn("Invalid direction", result)

    @patch('datetimetool.process_date.datetime')
    def test_get_start_of_period(self, mock_datetime):
        """Test get_start_of_period function"""
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.datetime.strptime.return_value.date.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_start_of_period('week')
        self.assertEqual(result, "14-07-2025")
        
        result = get_start_of_period('month')
        self.assertEqual(result, "01-07-2025")
        
        result = get_start_of_period('year')
        self.assertEqual(result, "01-01-2025")

    def test_get_start_of_period_invalid_period(self):
        """Test get_start_of_period function with invalid period"""
        result = get_start_of_period('invalid')
        self.assertIn("Invalid period", result)

    @patch('datetimetool.process_date.datetime')
    def test_get_end_of_period(self, mock_datetime):
        """Test get_end_of_period function"""
        # Mock current date as Friday, July 18, 2025
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.datetime.strptime.return_value.date.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_end_of_period('week')
        self.assertEqual(result, "20-07-2025")
        
        result = get_end_of_period('month')
        self.assertEqual(result, "31-07-2025")
        
        result = get_end_of_period('year')
        self.assertEqual(result, "31-12-2025")

    @patch('datetimetool.process_date.datetime')
    def test_get_date_range_for_week(self, mock_datetime):
        """Test get_date_range_for_week function"""
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_date_range_for_week(0)
        expected = {
            "start_date": "14-07-2025",
            "end_date": "20-07-2025"
        }
        self.assertEqual(result, expected)
        
        result = get_date_range_for_week(-1)
        expected = {
            "start_date": "07-07-2025",
            "end_date": "13-07-2025"
        }
        self.assertEqual(result, expected)

    @patch('datetimetool.process_date.relativedelta')
    @patch('datetimetool.process_date.datetime')
    def test_get_date_range_for_quarter(self, mock_datetime, mock_relativedelta):
        """Test get_date_range_for_quarter function"""
        from dateutil.relativedelta import relativedelta
        
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.date.side_effect = lambda *args: datetime.date(*args)
        mock_relativedelta.side_effect = lambda **kwargs: relativedelta(**kwargs)
        
        result = get_date_range_for_quarter(0)
        expected = {
            "start_date": "01-07-2025",
            "end_date": "30-09-2025"
        }
        self.assertEqual(result, expected)
        
        result = get_date_range_for_quarter(-1)
        expected = {
            "start_date": "01-04-2025",
            "end_date": "30-06-2025"
        }
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
