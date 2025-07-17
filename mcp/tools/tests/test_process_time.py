import unittest
import datetime
from unittest.mock import patch
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetimetool.process_time import (
    _is_numeric,
    _parse_numeric_string,
    _parse_time_query,
    calculate_time
)


class TestProcessTime(unittest.TestCase):
    """Unit tests for process_time.py module"""

    def test_is_numeric_with_valid_numbers(self):
        """Test _is_numeric function with valid numeric strings"""
        self.assertTrue(_is_numeric("123"))
        self.assertTrue(_is_numeric("0"))
        self.assertTrue(_is_numeric("999"))

    def test_is_numeric_with_invalid_inputs(self):
        """Test _is_numeric function with non-numeric strings"""
        self.assertFalse(_is_numeric("abc"))
        self.assertFalse(_is_numeric("12.5"))
        self.assertFalse(_is_numeric(""))
        self.assertFalse(_is_numeric("12a"))

    def test_parse_numeric_string_with_word_numbers(self):
        """Test _parse_numeric_string function with word-based numbers"""
        self.assertEqual(_parse_numeric_string("a couple of"), "2")
        self.assertEqual(_parse_numeric_string("a"), "1")
        self.assertEqual(_parse_numeric_string("the"), "1")
        self.assertEqual(_parse_numeric_string("5"), "5")

    def test_parse_time_query_hours_format(self):
        """Test _parse_time_query with hour-based queries"""
        result = _parse_time_query("2 hours ago")
        self.assertEqual(result, (2, 'hours', 'ago'))
        
        result = _parse_time_query("1 hr from now")
        self.assertEqual(result, (1, 'hours', 'from now'))

    def test_parse_time_query_minutes_format(self):
        """Test _parse_time_query with minute-based queries"""
        result = _parse_time_query("30 minutes ago")
        self.assertEqual(result, (30, 'minutes', 'ago'))
        
        result = _parse_time_query("5 mins from now")
        self.assertEqual(result, (5, 'minutes', 'from now'))

    def test_parse_time_query_seconds_format(self):
        """Test _parse_time_query with second-based queries"""
        result = _parse_time_query("45 seconds ago")
        self.assertEqual(result, (45, 'seconds', 'ago'))
        
        result = _parse_time_query("10 secs from now")
        self.assertEqual(result, (10, 'seconds', 'from now'))

    def test_parse_time_query_invalid_inputs(self):
        """Test _parse_time_query with invalid inputs"""
        self.assertIsNone(_parse_time_query("invalid query"))
        self.assertIsNone(_parse_time_query(""))
        self.assertIsNone(_parse_time_query(None))
        self.assertIsNone(_parse_time_query(123))

    @patch('datetimetool.process_time.datetime')
    def test_calculate_time_hours_ago(self, mock_datetime):
        """Test calculate_time function for hours ago calculation"""
        # Mock current time as 12:00:00
        mock_now = datetime.datetime(2025, 7, 17, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_time("2 hours ago")
        self.assertEqual(result, "10:00:00")

    @patch('datetimetool.process_time.datetime')
    def test_calculate_time_minutes_from_now(self, mock_datetime):
        """Test calculate_time function for minutes from now calculation"""
        # Mock current time as 14:30:00
        mock_now = datetime.datetime(2025, 7, 17, 14, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_time("15 minutes from now")
        self.assertEqual(result, "14:45:00")

    @patch('datetimetool.process_time.datetime')
    def test_calculate_time_seconds_calculation(self, mock_datetime):
        """Test calculate_time function for seconds calculation"""
        # Mock current time as 09:15:30
        mock_now = datetime.datetime(2025, 7, 17, 9, 15, 30)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_time("45 seconds ago")
        self.assertEqual(result, "09:14:45")

    def test_parse_time_query_edge_cases(self):
        """Test _parse_time_query with edge case inputs"""
        # Test alternative direction words
        result = _parse_time_query("in 5 minutes")
        self.assertEqual(result, (5, 'minutes', 'in'))
        
        result = _parse_time_query("after 2 hours")
        self.assertEqual(result, (2, 'hours', 'after'))
        
        result = _parse_time_query("before 30 seconds")
        self.assertEqual(result, (30, 'seconds', 'before'))

    def test_parse_time_query_word_numbers(self):
        """Test _parse_time_query with word-based numbers"""
        result = _parse_time_query("a couple of hours ago")
        self.assertEqual(result, (2, 'hours', 'ago'))
        
        result = _parse_time_query("a minute from now")
        self.assertEqual(result, (1, 'minutes', 'from now'))

    def test_parse_time_query_compact_format(self):
        """Test _parse_time_query with compact time formats (no spaces)"""
        result = _parse_time_query("10mins ago")
        self.assertEqual(result, (10, 'minutes', 'ago'))
        
        result = _parse_time_query("5hrs from now")
        self.assertEqual(result, (5, 'hours', 'from now'))

    @patch('datetimetool.process_time.datetime')
    def test_calculate_time_boundary_cases(self, mock_datetime):
        """Test calculate_time function with boundary time cases"""
        # Test midnight crossing (23:30 + 1 hour = 00:30 next day)
        mock_now = datetime.datetime(2025, 7, 17, 23, 30, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_time("1 hour from now")
        self.assertEqual(result, "00:30:00")

    @patch('datetimetool.process_time.datetime')
    def test_calculate_time_large_values(self, mock_datetime):
        """Test calculate_time function with large time values"""
        # Mock current time as 12:00:00
        mock_now = datetime.datetime(2025, 7, 17, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_time("120 minutes ago")
        self.assertEqual(result, "10:00:00")

    def test_calculate_time_invalid_query_handling(self):
        """Test calculate_time function with invalid queries"""
        result = calculate_time("invalid time query")
        self.assertEqual(result, "Invalid query format. Please use a valid format.")
        
        result = calculate_time("")
        self.assertEqual(result, "Invalid query format. Please use a valid format.")
        
        result = calculate_time("random text")
        self.assertEqual(result, "Invalid query format. Please use a valid format.")

    def test_parse_time_query_alternative_formats(self):
        """Test _parse_time_query with various alternative formats"""
        # Test different unit abbreviations
        result = _parse_time_query("3 sec ago")
        self.assertEqual(result, (3, 'seconds', 'ago'))
        
        result = _parse_time_query("2 hr from now")
        self.assertEqual(result, (2, 'hours', 'from now'))
        
        # Test with 'the' article
        result = _parse_time_query("the hour ago")
        self.assertEqual(result, (1, 'hours', 'ago'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
