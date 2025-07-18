import unittest
import datetime
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetimetool.process_time import (
    get_current_time,
    get_time_with_offset,
    get_time_range_for_day_part
)


class TestProcessTimeAtomic(unittest.TestCase):

    @patch('datetimetool.process_time.datetime')
    def test_get_current_time(self, mock_datetime):
        """Test get_current_time function"""
        mock_now = datetime.datetime(2025, 7, 18, 14, 30, 45)
        mock_datetime.datetime.now.return_value = mock_now
        
        result = get_current_time()
        self.assertEqual(result, "14:30:45")

    @patch('datetimetool.process_time.datetime')
    def test_get_time_with_offset_same_day_seconds(self, mock_datetime):
        """Test get_time_with_offset function with seconds on same day"""
        mock_now = datetime.datetime(2025, 7, 18, 14, 30, 45)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_time_with_offset(30, 'seconds')
        self.assertEqual(result, "14:31:15")
        
        result = get_time_with_offset(-45, 'seconds')
        self.assertEqual(result, "14:30:00")

    @patch('datetimetool.process_time.datetime')
    def test_get_time_with_offset_same_day_minutes(self, mock_datetime):
        """Test get_time_with_offset function with minutes on same day"""
        mock_now = datetime.datetime(2025, 7, 18, 14, 30, 45)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_time_with_offset(15, 'minutes')
        self.assertEqual(result, "14:45:45")
        
        result = get_time_with_offset(-30, 'minutes')
        self.assertEqual(result, "14:00:45")

    @patch('datetimetool.process_time.datetime')
    def test_get_time_with_offset_same_day_hours(self, mock_datetime):
        """Test get_time_with_offset function with hours on same day"""
        mock_now = datetime.datetime(2025, 7, 18, 14, 30, 45)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_time_with_offset(3, 'hours')
        self.assertEqual(result, "17:30:45")
        
        result = get_time_with_offset(-5, 'hours')
        self.assertEqual(result, "09:30:45")

    @patch('datetimetool.process_time.datetime')
    def test_get_time_with_offset_different_day(self, mock_datetime):
        """Test get_time_with_offset function crossing day boundary"""
        mock_now = datetime.datetime(2025, 7, 18, 14, 30, 45)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_time_with_offset(24, 'hours')
        self.assertEqual(result, "19-07-2025 14:30:45")
        
        result = get_time_with_offset(-24, 'hours')
        self.assertEqual(result, "17-07-2025 14:30:45")
        
        result = get_time_with_offset(10, 'hours')
        self.assertEqual(result, "19-07-2025 00:30:45")

    @patch('datetimetool.process_time.datetime')
    def test_get_time_with_offset_with_base_datetime_same_day(self, mock_datetime):
        """Test get_time_with_offset function with base datetime on same day"""
        base_dt = datetime.datetime(2025, 10, 1, 10, 0, 0)
        mock_datetime.datetime.strptime.return_value = base_dt
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_time_with_offset(90, 'minutes', base_datetime_str="01-10-2025 10:00:00")
        self.assertEqual(result, "11:30:00")
        
        result = get_time_with_offset(-2, 'hours', base_datetime_str="01-10-2025 10:00:00")
        self.assertEqual(result, "08:00:00")

    @patch('datetimetool.process_time.datetime')
    def test_get_time_with_offset_with_base_datetime_different_day(self, mock_datetime):
        """Test get_time_with_offset function with base datetime crossing days"""
        base_dt = datetime.datetime(2025, 10, 1, 10, 0, 0)
        mock_datetime.datetime.strptime.return_value = base_dt
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_time_with_offset(15, 'hours', base_datetime_str="01-10-2025 10:00:00")
        self.assertEqual(result, "02-10-2025 01:00:00")
        
        result = get_time_with_offset(-12, 'hours', base_datetime_str="01-10-2025 10:00:00")
        self.assertEqual(result, "30-09-2025 22:00:00")

    def test_get_time_with_offset_invalid_unit(self):
        """Test get_time_with_offset function with invalid unit"""
        result = get_time_with_offset(5, 'invalid')
        self.assertIn("Invalid unit", result)

    def test_get_time_with_offset_invalid_datetime_format(self):
        """Test get_time_with_offset function with invalid datetime format"""
        result = get_time_with_offset(5, 'minutes', base_datetime_str="2025-07-18 14:30:45")
        self.assertIn("Invalid base_datetime_str format", result)

    @patch('datetimetool.process_time.datetime')
    def test_get_time_range_for_day_part_morning(self, mock_datetime):
        """Test get_time_range_for_day_part function for morning"""
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        
        result = get_time_range_for_day_part('morning')
        expected = {
            "start_time": "18-07-2025 00:00:00",
            "end_time": "18-07-2025 11:59:59"
        }
        self.assertEqual(result, expected)

    @patch('datetimetool.process_time.datetime')
    def test_get_time_range_for_day_part_afternoon(self, mock_datetime):
        """Test get_time_range_for_day_part function for afternoon"""
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        
        result = get_time_range_for_day_part('afternoon')
        expected = {
            "start_time": "18-07-2025 12:00:00",
            "end_time": "18-07-2025 17:59:59"
        }
        self.assertEqual(result, expected)

    @patch('datetimetool.process_time.datetime')
    def test_get_time_range_for_day_part_evening(self, mock_datetime):
        """Test get_time_range_for_day_part function for evening"""
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        
        result = get_time_range_for_day_part('evening')
        expected = {
            "start_time": "18-07-2025 18:00:00",
            "end_time": "18-07-2025 23:59:59"
        }
        self.assertEqual(result, expected)

    @patch('datetimetool.process_time.datetime')
    def test_get_time_range_for_day_part_with_base_date(self, mock_datetime):
        """Test get_time_range_for_day_part function with specific base date"""
        base_date = datetime.date(2025, 12, 25)
        mock_datetime.datetime.strptime.return_value.date.return_value = base_date
        
        result = get_time_range_for_day_part('morning', base_date_str="25-12-2025")
        expected = {
            "start_time": "25-12-2025 00:00:00",
            "end_time": "25-12-2025 11:59:59"
        }
        self.assertEqual(result, expected)

    def test_get_time_range_for_day_part_invalid_part(self):
        """Test get_time_range_for_day_part function with invalid part of day"""
        result = get_time_range_for_day_part('invalid')
        self.assertIn("Invalid part_of_day", result)

    def test_get_time_range_for_day_part_invalid_date_format(self):
        """Test get_time_range_for_day_part function with invalid date format"""
        result = get_time_range_for_day_part('morning', base_date_str="2025-07-18")
        self.assertIn("Invalid date format", result)

    @patch('datetimetool.process_time.datetime')
    def test_get_time_range_for_day_part_case_insensitive(self, mock_datetime):
        """Test get_time_range_for_day_part function is case insensitive"""
        mock_today = datetime.date(2025, 7, 18)
        mock_datetime.date.today.return_value = mock_today
        
        result = get_time_range_for_day_part('MORNING')
        expected = {
            "start_time": "18-07-2025 00:00:00",
            "end_time": "18-07-2025 11:59:59"
        }
        self.assertEqual(result, expected)
        
        result = get_time_range_for_day_part('AfTeRnOoN')
        expected = {
            "start_time": "18-07-2025 12:00:00",
            "end_time": "18-07-2025 17:59:59"
        }
        self.assertEqual(result, expected)

    @patch('datetimetool.process_time.datetime')
    def test_edge_case_midnight_crossing(self, mock_datetime):
        """Test edge cases around midnight crossing"""
        mock_now = datetime.datetime(2025, 7, 18, 23, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = get_time_with_offset(1, 'hours')
        self.assertEqual(result, "19-07-2025 00:30:00")
        
        mock_now = datetime.datetime(2025, 7, 18, 0, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        result = get_time_with_offset(-1, 'hours')
        self.assertEqual(result, "17-07-2025 23:30:00")


if __name__ == '__main__':
    unittest.main()
