import unittest
import datetime
from unittest.mock import patch
import sys
import os

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetimetool.process_date import (
    _is_numeric,
    _parse_numeric_string,
    _parse_date_query,
    calculate_date
)


class TestProcessDate(unittest.TestCase):
    """Unit tests for process_date.py module"""

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

    def test_parse_date_query_special_keywords(self):
        """Test _parse_date_query with special keyword queries"""
        self.assertEqual(_parse_date_query("tomorrow"), (1, 'days', 'from now'))
        self.assertEqual(_parse_date_query("yesterday"), (1, 'days', 'ago'))
        self.assertEqual(_parse_date_query("day after tomorrow"), (2, 'days', 'from now'))
        self.assertEqual(_parse_date_query("day before yesterday"), (2, 'days', 'ago'))

    def test_parse_date_query_next_last_patterns(self):
        """Test _parse_date_query with next/last patterns"""
        self.assertEqual(_parse_date_query("next week"), (1, 'week', 'next'))
        self.assertEqual(_parse_date_query("last month"), (1, 'month', 'last'))
        self.assertEqual(_parse_date_query("next friday"), (1, 'friday', 'next'))

    def test_parse_date_query_numeric_patterns(self):
        """Test _parse_date_query with numeric time patterns"""
        self.assertEqual(_parse_date_query("3 months ago"), (3, 'month', 'ago'))
        self.assertEqual(_parse_date_query("2 weeks from now"), (2, 'week', 'from now'))
        self.assertEqual(_parse_date_query("5 days before"), (5, 'day', 'before'))

    def test_parse_date_query_invalid_inputs(self):
        """Test _parse_date_query with invalid inputs"""
        self.assertIsNone(_parse_date_query("invalid query"))
        self.assertIsNone(_parse_date_query(""))
        self.assertIsNone(_parse_date_query(None))
        self.assertIsNone(_parse_date_query(123))

    @patch('datetimetool.process_date.datetime')
    def test_calculate_date_days_ago(self, mock_datetime):
        """Test calculate_date function for days ago calculation"""
        # Mock current date as 2025-07-17
        mock_today = datetime.date(2025, 7, 17)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_date("3 days ago")
        self.assertEqual(result, "2025-07-14")

    @patch('datetimetool.process_date.datetime')
    def test_calculate_date_weeks_from_now(self, mock_datetime):
        """Test calculate_date function for weeks from now calculation"""
        # Mock current date as 2025-07-17
        mock_today = datetime.date(2025, 7, 17)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_date("2 weeks from now")
        self.assertEqual(result, "2025-07-31")

    @patch('datetimetool.process_date.datetime')
    def test_calculate_date_tomorrow_yesterday(self, mock_datetime):
        """Test calculate_date function for tomorrow and yesterday"""
        # Mock current date as 2025-07-17
        mock_today = datetime.date(2025, 7, 17)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result_tomorrow = calculate_date("tomorrow")
        self.assertEqual(result_tomorrow, "2025-07-18")
        
        result_yesterday = calculate_date("yesterday")
        self.assertEqual(result_yesterday, "2025-07-16")

    def test_parse_date_query_fortnight_cases(self):
        """Test _parse_date_query with fortnight patterns"""
        result = _parse_date_query("a fortnight from now")
        self.assertEqual(result, (2, 'weeks', 'from now'))
        
        result = _parse_date_query("fortnight ago")
        self.assertEqual(result, (2, 'weeks', 'ago'))

    def test_parse_date_query_word_numbers(self):
        """Test _parse_date_query with word-based numbers"""
        result = _parse_date_query("a couple of days ago")
        self.assertEqual(result, (2, 'day', 'ago'))
        
        result = _parse_date_query("a year from now")
        self.assertEqual(result, (1, 'year', 'from now'))

    def test_parse_date_query_alternative_directions(self):
        """Test _parse_date_query with alternative direction words"""
        result = _parse_date_query("in 3 weeks")
        self.assertEqual(result, (3, 'w', 'in'))
        
        result = _parse_date_query("back 5 days")
        self.assertEqual(result, (5, 'd', 'back'))

    def test_parse_date_query_compact_formats(self):
        """Test _parse_date_query with compact date formats"""
        result = _parse_date_query("5d ago")
        self.assertEqual(result, (5, 'd', 'ago'))
        
        result = _parse_date_query("2w from now")
        self.assertEqual(result, (2, 'w', 'from now'))
        
        result = _parse_date_query("1y before")
        self.assertEqual(result, (1, 'y', 'before'))

    @patch('datetimetool.process_date.datetime')
    def test_calculate_date_months_calculation(self, mock_datetime):
        """Test calculate_date function for month calculations"""
        # Mock current date as 2025-07-17
        mock_today = datetime.date(2025, 7, 17)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_date("6 months ago")
        self.assertEqual(result, "2025-01-17")
        
        result = calculate_date("3 months from now")
        self.assertEqual(result, "2025-10-17")

    @patch('datetimetool.process_date.datetime')
    def test_calculate_date_months_from_now_and_ago(self, mock_datetime):
        """Test calculate_date function for various month calculations from now and ago"""
        # Mock current date as 2025-07-17 (mid-year)
        mock_today = datetime.date(2025, 7, 17)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_date("1 month ago")
        self.assertEqual(result, "2025-06-17")
        
        result = calculate_date("18 months ago")
        self.assertEqual(result, "2024-01-17")
        
        result = calculate_date("1 month from now")
        self.assertEqual(result, "2025-08-17")
        
        result = calculate_date("15 months from now")
        self.assertEqual(result, "2026-10-17")
        
        result = calculate_date("4 mos ago")
        self.assertEqual(result, "2025-03-17")
        
        result = calculate_date("8 mos from now")
        self.assertEqual(result, "2026-03-17")

    @patch('datetimetool.process_date.datetime')
    def test_calculate_date_years_calculation(self, mock_datetime):
        """Test calculate_date function for year calculations"""
        # Mock current date as 2025-07-17
        mock_today = datetime.date(2025, 7, 17)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_date("2 years ago")
        self.assertEqual(result, "2023-07-17")
        
        result = calculate_date("1 year from now")
        self.assertEqual(result, "2026-07-17")

    @patch('datetimetool.process_date.datetime')
    def test_calculate_date_weekday_calculations(self, mock_datetime):
        """Test calculate_date function for weekday calculations"""
        # Mock current date as 2025-07-17 (Thursday)
        mock_today = datetime.date(2025, 7, 17)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_date("next monday")
        self.assertEqual(result, "2025-07-21")
        
        result = calculate_date("last friday")
        self.assertEqual(result, "2025-07-11")

    def test_calculate_date_invalid_query_handling(self):
        """Test calculate_date function with invalid queries"""
        result = calculate_date("invalid date query")
        self.assertEqual(result, "Invalid query format. Please use a valid format.")
        
        result = calculate_date("")
        self.assertEqual(result, "Invalid query format. Please use a valid format.")
        
        result = calculate_date("random text")
        self.assertEqual(result, "Invalid query format. Please use a valid format.")

    def test_parse_date_query_special_day_combinations(self):
        """Test _parse_date_query with special day combinations"""
        result = _parse_date_query("day after tomorrow")
        self.assertEqual(result, (2, 'days', 'from now'))
        
        result = _parse_date_query("day before yesterday")
        self.assertEqual(result, (2, 'days', 'ago'))

    @patch('datetimetool.process_date.datetime')
    def test_calculate_date_boundary_cases(self, mock_datetime):
        """Test calculate_date function with boundary date cases"""
        # Test year boundary crossing
        mock_today = datetime.date(2025, 12, 31)
        mock_datetime.date.today.return_value = mock_today
        mock_datetime.timedelta = datetime.timedelta
        
        result = calculate_date("1 day from now")
        self.assertEqual(result, "2026-01-01")

    def test_parse_date_query_unit_variations(self):
        """Test _parse_date_query with various unit abbreviations"""
        result = _parse_date_query("3 mos ago")
        self.assertEqual(result, (3, 'mo', 'ago'))
        
        result = _parse_date_query("2 yrs from now")
        self.assertEqual(result, (2, 'yr', 'from now'))
        
        result = _parse_date_query("5 wks before")
        self.assertEqual(result, (5, 'wk', 'before'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
