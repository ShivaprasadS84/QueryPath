"""
Complex Date Parsing System for Medical Query Strings
=====================================================

This module provides a sophisticated date parsing system that extracts temporal information
from natural language medical queries and returns structured JSON with either single dates
or date ranges based on the context.

Author: AI Assistant
Date: July 2025
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
import calendar


@dataclass
class DateRange:
    """Represents a date range with start and end dates."""
    start_date: datetime
    end_date: datetime

    def to_dict(self) -> Dict:
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat()
        }


@dataclass
class SingleDate:
    """Represents a single specific date."""
    date: datetime

    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat()
        }


class ComplexDateParser:
    """
    A complex date parsing system that handles various temporal expressions
    in medical query strings and returns structured JSON output.
    """

    def __init__(self, reference_date: Optional[datetime] = None):
        """
        Initialize the date parser with a reference date.

        Args:
            reference_date: The reference date for relative calculations.
                          Defaults to current date.
        """
        self.reference_date = reference_date or datetime.now()
        self._setup_patterns()

    def _setup_patterns(self):
        """Set up regex patterns for different types of temporal expressions."""

        # Number word mapping
        self.number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20
        }

        # Relative time patterns
        self.relative_patterns = {
            # Past patterns with numbers
            r'in the past (\d+) days?': ('days', 'past'),
            r'in the past (\d+) weeks?': ('weeks', 'past'),
            r'in the past (\d+) months?': ('months', 'past'),
            r'in the past (\d+) years?': ('years', 'past'),
            r'from the past (\d+) days?': ('days', 'past'),
            r'from the past (\d+) weeks?': ('weeks', 'past'),
            r'from the past (\d+) months?': ('months', 'past'),
            r'from the past (\d+) years?': ('years', 'past'),
            r'last (\d+) days?': ('days', 'past'),
            r'last (\d+) weeks?': ('weeks', 'past'),
            r'last (\d+) months?': ('months', 'past'),
            r'last (\d+) years?': ('years', 'past'),
            r'from the last (\d+) days?': ('days', 'past'),
            r'from the last (\d+) weeks?': ('weeks', 'past'),
            r'from the last (\d+) months?': ('months', 'past'),
            r'from the last (\d+) years?': ('years', 'past'),
            r'within the last (\d+) days?': ('days', 'past'),
            r'within the last (\d+) weeks?': ('weeks', 'past'),
            r'within the last (\d+) months?': ('months', 'past'),
            r'within the last (\d+) years?': ('years', 'past'),
            r'previous (\d+) days?': ('days', 'past'),
            r'previous (\d+) weeks?': ('weeks', 'past'),
            r'previous (\d+) months?': ('months', 'past'),
            r'previous (\d+) years?': ('years', 'past'),
            r'from the previous (\d+) days?': ('days', 'past'),
            r'from the previous (\d+) weeks?': ('weeks', 'past'),
            r'from the previous (\d+) months?': ('months', 'past'),
            r'from the previous (\d+) years?': ('years', 'past'),
            # Additional common patterns
            r'past (\d+) days?': ('days', 'past'),
            r'past (\d+) weeks?': ('weeks', 'past'),
            r'past (\d+) months?': ('months', 'past'),
            r'past (\d+) years?': ('years', 'past'),
            # Written numbers
            r'in the past (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) days?': ('days', 'past'),
            r'in the past (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) weeks?': ('weeks', 'past'),
            r'in the past (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) months?': ('months', 'past'),
            r'in the past (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) years?': ('years', 'past'),
            r'from the last (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) days?': ('days', 'past'),
            r'from the last (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) weeks?': ('weeks', 'past'),
            r'from the last (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) months?': ('months', 'past'),
            r'from the last (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) years?': ('years', 'past'),
            r'past (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) days?': ('days', 'past'),
            r'past (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) weeks?': ('weeks', 'past'),
            r'past (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) months?': ('months', 'past'),
            r'past (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) years?': ('years', 'past'),
            r'previous (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) days?': ('days', 'past'),
            r'previous (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) weeks?': ('weeks', 'past'),
            r'previous (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) months?': ('months', 'past'),
            r'previous (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) years?': ('years', 'past'),
            # Patterns with "last" for written numbers
            r'last (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) days?': ('days', 'past'),
            r'last (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) weeks?': ('weeks', 'past'),
            r'last (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) months?': ('months', 'past'),
            r'last (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) years?': ('years', 'past'),
            # "Ago" patterns with numbers
            r'(\d+) days? ago': ('days', 'past'),
            r'(\d+) weeks? ago': ('weeks', 'past'),
            r'(\d+) months? ago': ('months', 'past'),
            r'(\d+) years? ago': ('years', 'past'),
            # "Ago" patterns with written numbers
            r'(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) days? ago': ('days', 'past'),
            r'(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) weeks? ago': ('weeks', 'past'),
            r'(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) months? ago': ('months', 'past'),
            r'(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) years? ago': ('years', 'past'),
        }

        # Named relative periods
        self.named_periods = {
            r'\bthe day before yesterday\b': ('days', 2, 'specific_past'),
            r'\bday before yesterday\b': ('days', 2, 'specific_past'),
            r'\byesterday\b': ('days', 1, 'specific_past'),
            r'\btoday\b': ('days', 0, 'specific'),
            r'\blast week\b': ('weeks', 1, 'specific_past'),
            r'\bprevious week\b': ('weeks', 1, 'specific_past'),
            r'\bthis week\b': ('weeks', 0, 'specific'),
            r'\blast month\b': ('months', 1, 'specific_past'),
            r'\bprevious month\b': ('months', 1, 'specific_past'),
            r'\bthis month\b': ('months', 0, 'specific'),
            r'\blast year\b': ('years', 1, 'specific_past'),
            r'\bprevious year\b': ('years', 1, 'specific_past'),
            r'\bthis year\b': ('years', 0, 'specific'),
            r'\blast monday\b': ('monday', 1, 'specific_past'),
            r'\blast tuesday\b': ('tuesday', 1, 'specific_past'),
            r'\blast wednesday\b': ('wednesday', 1, 'specific_past'),
            r'\blast thursday\b': ('thursday', 1, 'specific_past'),
            r'\blast friday\b': ('friday', 1, 'specific_past'),
            r'\blast saturday\b': ('saturday', 1, 'specific_past'),
            r'\blast sunday\b': ('sunday', 1, 'specific_past'),
        }

        # Bare weekday patterns (without "last")
        self.weekday_patterns = {
            r'\bmonday\b': ('monday', 1, 'specific_past'),
            r'\btuesday\b': ('tuesday', 1, 'specific_past'),
            r'\bwednesday\b': ('wednesday', 1, 'specific_past'),
            r'\bthursday\b': ('thursday', 1, 'specific_past'),
            r'\bfriday\b': ('friday', 1, 'specific_past'),
            r'\bsaturday\b': ('saturday', 1, 'specific_past'),
            r'\bsunday\b': ('sunday', 1, 'specific_past'),
        }

        # Quarter patterns
        self.quarter_patterns = {
            r'\bfirst quarter\b': 'Q1',
            r'\bsecond quarter\b': 'Q2',
            r'\bthird quarter\b': 'Q3',
            r'\bfourth quarter\b': 'Q4',
            r'\bcurrent quarter\b': 'current',
            r'\blast quarter\b': 'last',
            r'\bprevious quarter\b': 'last',
        }

        # Month patterns
        self.month_patterns = {
            r'\bjanuary\b': 1, r'\bjan\b': 1,
            r'\bfebruary\b': 2, r'\bfeb\b': 2,
            r'\bmarch\b': 3, r'\bmar\b': 3,
            r'\bapril\b': 4, r'\bapr\b': 4,
            r'\bmay\b': 5,
            r'\bjune\b': 6, r'\bjun\b': 6,
            r'\bjuly\b': 7, r'\bjul\b': 7,
            r'\baugust\b': 8, r'\baug\b': 8,
            r'\bseptember\b': 9, r'\bsep\b': 9, r'\bsept\b': 9,
            r'\boctober\b': 10, r'\boct\b': 10,
            r'\bnovember\b': 11, r'\bnov\b': 11,
            r'\bdecember\b': 12, r'\bdec\b': 12
        }

        # Specific date patterns
        self.specific_date_patterns = [
            r'(\d{1,2})(st|nd|rd|th)?\s+of\s+(\w+)\s+(?:this\s+)?year',  # "4th of July this year"
            r'(\w+)\s+(\d{1,2})(st|nd|rd|th)?(?:\s+this\s+year)?',       # "July 4th" or "July 4th this year"
            r'(\d{1,2})(st|nd|rd|th)?\s+of\s+this\s+month',              # "1st of this month"
            r'on\s+the\s+(\d{1,2})(st|nd|rd|th)?\s+of\s+this\s+month',   # "on the 1st of this month"
            r'(\w+)\s+(\d{1,2})(st|nd|rd|th)?,?\s+(\d{4})',              # "July 1st, 2024" or "July 1st 2024"
            r'(\d{1,2})(st|nd|rd|th)?\s+of\s+(\w+),?\s+(\d{4})',         # "1st of July, 2024" or "1st of July 2024"
        ]

        # Date range patterns
        self.date_range_patterns = [
            # Date to date patterns
            r'from\s+(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+to\s+(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+(?:this\s+)?year',  # "from January 15th to March 15th this year"
            r'from\s+(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+to\s+(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+last\s+year',       # "from January 15th to March 15th last year"
            r'(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+to\s+(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+(?:this\s+)?year',        # "January 15th to March 15th this year"
            r'(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+to\s+(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+last\s+year',             # "January 15th to March 15th last year"
            # Month to month patterns
            r'from\s+(\w+)\s+to\s+(\w+)\s+(?:this\s+)?year',                                                      # "from March to August this year"
            r'from\s+(\w+)\s+to\s+(\w+)\s+last\s+year',                                                           # "from March to August last year"
            r'from\s+(\w+)\s+to\s+(\w+)',                                                                         # "from March to August" (defaults to this year)
            r'(\w+)\s+to\s+(\w+)\s+(?:this\s+)?year',                                                             # "March to August this year"
            r'(\w+)\s+to\s+(\w+)\s+last\s+year',                                                                  # "March to August last year"
        ]

        # Ordinal patterns for complex expressions
        self.ordinal_patterns = {
            r'second\s+(\w+)\s+of\s+last\s+month': 'second_weekday_last_month',
            r'last\s+day\s+of\s+the\s+previous\s+quarter': 'last_day_previous_quarter',
        }

        # Additional complex patterns for medical queries
        self.medical_time_patterns = {
            r'submitted\s+in\s+the\s+last\s+(\d+)\s+days?': ('days', 'past'),
            r'reported\s+in\s+the\s+last\s+(\d+)\s+days?': ('days', 'past'),
            r'submitted\s+in\s+the\s+last\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\s+days?': ('days', 'past'),
            r'reported\s+in\s+the\s+last\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\s+days?': ('days', 'past'),
        }

    def parse_date_expression(self, text: str) -> Dict:
        """
        Parse a date expression from text and return structured JSON.

        Args:
            text: The input text containing date expressions

        Returns:
            Dict: Structured JSON with date information
        """
        text_lower = text.lower()

        # Try ordinal expressions first (they're more specific)
        ordinal_result = self._parse_ordinal_expressions(text_lower)
        if ordinal_result:
            return ordinal_result

        # Try date range patterns before specific dates
        range_specific_result = self._parse_date_ranges(text_lower)
        if range_specific_result:
            return range_specific_result

        # Try to parse specific dates
        specific_result = self._parse_specific_dates(text_lower)
        if specific_result:
            return specific_result

        # Try relative date ranges
        range_result = self._parse_relative_ranges(text_lower)
        if range_result:
            return range_result

        # Try medical patterns
        medical_result = self._parse_medical_patterns(text_lower)
        if medical_result:
            return medical_result

        # Try named periods
        named_result = self._parse_named_periods(text_lower)
        if named_result:
            return named_result

        # Try quarters
        quarter_result = self._parse_quarters(text_lower)
        if quarter_result:
            return quarter_result

        return {
            "type": "unparseable",
            "original_text": text,
            "error": "Could not parse date expression"
        }

    def _parse_specific_dates(self, text: str) -> Optional[Dict]:
        """Parse specific date mentions like 'July 4th this year'."""

        # Pattern: "4th of July this year"
        match = re.search(r'(\d{1,2})(st|nd|rd|th)?\s+of\s+(\w+)\s+(?:this\s+)?year', text)
        if match:
            day = int(match.group(1))
            month_name = match.group(3)
            month = self._get_month_number(month_name)
            if month:
                try:
                    specific_date = datetime(self.reference_date.year, month, day)
                    return {
                        "type": "single_date",
                        "date_type": "specific",
                        "original_text": match.group(0),
                        **SingleDate(specific_date).to_dict()
                    }
                except ValueError:
                    pass

        # Pattern: "on the 1st of this month"
        match = re.search(r'(?:on\s+the\s+)?(\d{1,2})(st|nd|rd|th)?\s+of\s+this\s+month', text)
        if match:
            day = int(match.group(1))
            try:
                specific_date = datetime(self.reference_date.year, self.reference_date.month, day)
                return {
                    "type": "single_date",
                    "date_type": "specific",
                    "original_text": match.group(0),
                    **SingleDate(specific_date).to_dict()
                }
            except ValueError:
                pass

        # Pattern: "January 15th this year"
        match = re.search(r'(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+this\s+year', text)
        if match:
            month_name = match.group(1)
            day = int(match.group(2))
            month = self._get_month_number(month_name)
            if month:
                try:
                    specific_date = datetime(self.reference_date.year, month, day)
                    return {
                        "type": "single_date",
                        "date_type": "specific",
                        "original_text": match.group(0),
                        **SingleDate(specific_date).to_dict()
                    }
                except ValueError:
                    pass

        return None

    def _parse_date_ranges(self, text: str) -> Optional[Dict]:
        """Parse date range patterns like 'from January 15th to March 15th this year'."""

        for pattern in self.date_range_patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()

                # Determine if this is a month-to-month pattern or date-to-date pattern
                # Month-to-month patterns have only 2 groups (start_month, end_month)
                # Date-to-date patterns have 4+ groups (start_month, start_day, end_month, end_day)

                if len(groups) == 2:
                    # Month to month patterns like "from March to August"
                    start_month_name = groups[0]
                    end_month_name = groups[1]

                    start_month = self._get_month_number(start_month_name)
                    end_month = self._get_month_number(end_month_name)

                    if start_month and end_month:
                        # Determine year
                        if 'last year' in match.group(0):
                            year = self.reference_date.year - 1
                        else:
                            year = self.reference_date.year

                        # Start of start month
                        start_date = datetime(year, start_month, 1, 0, 0, 0, 0)
                        # End of end month
                        last_day = calendar.monthrange(year, end_month)[1]
                        end_date = datetime(year, end_month, last_day, 23, 59, 59, 999999)

                        return {
                            "type": "date_range",
                            "date_type": "month_range",
                            "original_text": match.group(0),
                            **DateRange(start_date, end_date).to_dict()
                        }

                elif len(groups) >= 4:
                    # Date to date patterns like "from January 15th to March 15th"
                    # Extract month names and day numbers
                    start_month_name = groups[0]
                    start_day = int(groups[1])

                    # Find the end month and day (skip ordinals like "st", "nd", "rd", "th")
                    if len(groups) == 6:  # Pattern with ordinals: month, day, ordinal, month, day, ordinal
                        end_month_name = groups[3]
                        end_day = int(groups[4])
                    else:  # Pattern without ordinals or different structure
                        end_month_name = groups[2] if len(groups) > 2 else groups[0]
                        end_day = int(groups[3]) if len(groups) > 3 else int(groups[1])

                    start_month = self._get_month_number(start_month_name)
                    end_month = self._get_month_number(end_month_name)

                    if start_month and end_month:
                        # Determine year
                        if 'last year' in match.group(0):
                            year = self.reference_date.year - 1
                        else:
                            year = self.reference_date.year

                        try:
                            start_date = datetime(year, start_month, start_day, 0, 0, 0, 0)
                            end_date = datetime(year, end_month, end_day, 23, 59, 59, 999999)

                            return {
                                "type": "date_range",
                                "date_type": "specific_range",
                                "original_text": match.group(0),
                                **DateRange(start_date, end_date).to_dict()
                            }
                        except ValueError:
                            pass

        return None

    def _parse_specific_dates(self, text: str) -> Optional[Dict]:
        """Parse specific date mentions like 'July 4th this year'."""

        # Pattern: "4th of July this year"
        match = re.search(r'(\d{1,2})(st|nd|rd|th)?\s+of\s+(\w+)\s+(?:this\s+)?year', text)
        if match:
            day = int(match.group(1))
            month_name = match.group(3)
            month = self._get_month_number(month_name)
            if month:
                try:
                    specific_date = datetime(self.reference_date.year, month, day)
                    return {
                        "type": "single_date",
                        "date_type": "specific",
                        "original_text": match.group(0),
                        **SingleDate(specific_date).to_dict()
                    }
                except ValueError:
                    pass

        # Pattern: "4th of July last year"
        match = re.search(r'(\d{1,2})(st|nd|rd|th)?\s+of\s+(\w+)\s+last\s+year', text)
        if match:
            day = int(match.group(1))
            month_name = match.group(3)
            month = self._get_month_number(month_name)
            if month:
                try:
                    specific_date = datetime(self.reference_date.year - 1, month, day)
                    return {
                        "type": "single_date",
                        "date_type": "specific",
                        "original_text": match.group(0),
                        **SingleDate(specific_date).to_dict()
                    }
                except ValueError:
                    pass

        # Pattern: "on the 1st of this month"
        match = re.search(r'(?:on\s+the\s+)?(\d{1,2})(st|nd|rd|th)?\s+of\s+this\s+month', text)
        if match:
            day = int(match.group(1))
            try:
                specific_date = datetime(self.reference_date.year, self.reference_date.month, day)
                return {
                    "type": "single_date",
                    "date_type": "specific",
                    "original_text": match.group(0),
                    **SingleDate(specific_date).to_dict()
                }
            except ValueError:
                pass

        # Pattern: "January 15th this year"
        match = re.search(r'(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+this\s+year', text)
        if match:
            month_name = match.group(1)
            day = int(match.group(2))
            month = self._get_month_number(month_name)
            if month:
                try:
                    specific_date = datetime(self.reference_date.year, month, day)
                    return {
                        "type": "single_date",
                        "date_type": "specific",
                        "original_text": match.group(0),
                        **SingleDate(specific_date).to_dict()
                    }
                except ValueError:
                    pass

        # Pattern: "January 15th last year"
        match = re.search(r'(\w+)\s+(\d{1,2})(st|nd|rd|th)?\s+last\s+year', text)
        if match:
            month_name = match.group(1)
            day = int(match.group(2))
            month = self._get_month_number(month_name)
            if month:
                try:
                    specific_date = datetime(self.reference_date.year - 1, month, day)
                    return {
                        "type": "single_date",
                        "date_type": "specific",
                        "original_text": match.group(0),
                        **SingleDate(specific_date).to_dict()
                    }
                except ValueError:
                    pass

        # Pattern: "July 1st, 2024" or "July 1st 2024"
        match = re.search(r'(\w+)\s+(\d{1,2})(st|nd|rd|th)?,?\s+(\d{4})', text)
        if match:
            month_name = match.group(1)
            day = int(match.group(2))
            year = int(match.group(4))
            month = self._get_month_number(month_name)
            if month:
                try:
                    specific_date = datetime(year, month, day)
                    return {
                        "type": "single_date",
                        "date_type": "specific",
                        "original_text": match.group(0),
                        **SingleDate(specific_date).to_dict()
                    }
                except ValueError:
                    pass

        # Pattern: "1st of July, 2024" or "1st of July 2024"
        match = re.search(r'(\d{1,2})(st|nd|rd|th)?\s+of\s+(\w+),?\s+(\d{4})', text)
        if match:
            day = int(match.group(1))
            month_name = match.group(3)
            year = int(match.group(4))
            month = self._get_month_number(month_name)
            if month:
                try:
                    specific_date = datetime(year, month, day)
                    return {
                        "type": "single_date",
                        "date_type": "specific",
                        "original_text": match.group(0),
                        **SingleDate(specific_date).to_dict()
                    }
                except ValueError:
                    pass

        # Pattern: "July 1st" (without year, defaults to current year)
        match = re.search(r'(\w+)\s+(\d{1,2})(st|nd|rd|th)?(?!\s*(?:this|last|,?\s*\d{4}))', text)
        if match:
            month_name = match.group(1)
            day = int(match.group(2))
            month = self._get_month_number(month_name)
            if month:
                try:
                    specific_date = datetime(self.reference_date.year, month, day)
                    return {
                        "type": "single_date",
                        "date_type": "specific",
                        "original_text": match.group(0),
                        **SingleDate(specific_date).to_dict()
                    }
                except ValueError:
                    pass

        return None

    def _parse_relative_ranges(self, text: str) -> Optional[Dict]:
        """Parse relative date ranges like 'past 2 months', 'last 90 days'."""

        for pattern, (unit, direction) in self.relative_patterns.items():
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1)

                # Convert word numbers to integers
                if amount_str.isdigit():
                    amount = int(amount_str)
                else:
                    amount = self.number_words.get(amount_str.lower(), 0)
                    if amount == 0:
                        continue

                start_date, end_date = self._calculate_relative_range(amount, unit, direction)

                return {
                    "type": "date_range",
                    "date_type": "relative_range",
                    "original_text": match.group(0),
                    "amount": amount,
                    "unit": unit,
                    "direction": direction,
                    **DateRange(start_date, end_date).to_dict()
                }

        return None

    def _parse_medical_patterns(self, text: str) -> Optional[Dict]:
        """Parse medical-specific patterns like 'submitted in the last X days'."""

        # Check for medical time patterns
        for pattern, (unit, direction) in self.medical_time_patterns.items():
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1)

                # Convert word numbers to integers
                if amount_str.isdigit():
                    amount = int(amount_str)
                else:
                    amount = self.number_words.get(amount_str.lower(), 0)
                    if amount == 0:
                        continue

                start_date, end_date = self._calculate_relative_range(amount, unit, direction)

                return {
                    "type": "date_range",
                    "date_type": "relative_range",
                    "original_text": match.group(0),
                    "amount": amount,
                    "unit": unit,
                    "direction": direction,
                    **DateRange(start_date, end_date).to_dict()
                }

        return None

    def _parse_named_periods(self, text: str) -> Optional[Dict]:
        """Parse named periods like 'yesterday', 'last week', 'this month'."""

        # Check for named periods first
        for pattern, (unit, amount, period_type) in self.named_periods.items():
            match = re.search(pattern, text)
            if match:
                if period_type == 'specific':
                    if unit == 'days' and amount == 0:  # today
                        return {
                            "type": "single_date",
                            "date_type": "specific",
                            "original_text": match.group(0),
                            **SingleDate(self.reference_date.replace(hour=0, minute=0, second=0, microsecond=0)).to_dict()
                        }
                    elif unit == 'months' and amount == 0:  # this month
                        start_date, end_date = self._get_month_range(self.reference_date.year, self.reference_date.month)
                        return {
                            "type": "date_range",
                            "date_type": "named_period",
                            "original_text": match.group(0),
                            **DateRange(start_date, end_date).to_dict()
                        }
                elif period_type == 'specific_past':
                    if unit == 'days' and amount == 1:  # yesterday
                        yesterday = self.reference_date - timedelta(days=1)
                        return {
                            "type": "single_date",
                            "date_type": "specific_past",
                            "original_text": match.group(0),
                            **SingleDate(yesterday.replace(hour=0, minute=0, second=0, microsecond=0)).to_dict()
                        }
                    elif unit == 'days' and amount == 2:  # the day before yesterday
                        day_before_yesterday = self.reference_date - timedelta(days=2)
                        return {
                            "type": "single_date",
                            "date_type": "specific_past",
                            "original_text": match.group(0),
                            **SingleDate(day_before_yesterday.replace(hour=0, minute=0, second=0, microsecond=0)).to_dict()
                        }
                    elif unit.endswith('day'):  # last Monday, Tuesday, etc.
                        weekday = unit  # Use the full weekday name directly
                        last_weekday = self._get_last_weekday(weekday)

                        if last_weekday:
                            original_text = match.group(0)
                            return {
                                "type": "single_date",
                                "date_type": "specific_past",
                                "original_text": original_text,
                                **SingleDate(last_weekday).to_dict()
                            }
                    elif unit == 'months' and amount == 1:  # last month or previous month
                        start_date, end_date = self._get_last_month_range()
                        return {
                            "type": "date_range",
                            "date_type": "named_period",
                            "original_text": match.group(0),
                            **DateRange(start_date, end_date).to_dict()
                        }
                    elif unit == 'weeks' and amount == 1:  # last week or previous week
                        start_date, end_date = self._get_last_week_range()
                        return {
                            "type": "date_range",
                            "date_type": "named_period",
                            "original_text": match.group(0),
                            **DateRange(start_date, end_date).to_dict()
                        }
                    elif unit == 'years' and amount == 1:  # last year or previous year
                        start_date, end_date = self._get_last_year_range()
                        return {
                            "type": "date_range",
                            "date_type": "named_period",
                            "original_text": match.group(0),
                            **DateRange(start_date, end_date).to_dict()
                        }

        # Check for bare weekdays (not preceded by "last")
        for pattern, (unit, amount, period_type) in self.weekday_patterns.items():
            match = re.search(pattern, text)
            if match:
                # Make sure it's not preceded by "last"
                full_match = match.group(0)
                start_pos = match.start()

                # Check if "last" appears immediately before this weekday
                prefix_text = text[:start_pos].strip()
                words_before = prefix_text.split()

                # Only process bare weekdays (not preceded by "last")
                if not words_before or words_before[-1] != 'last':
                    weekday = unit
                    last_weekday = self._get_last_weekday(weekday)

                    if last_weekday:
                        return {
                            "type": "single_date",
                            "date_type": "specific_past",
                            "original_text": full_match,
                            **SingleDate(last_weekday).to_dict()
                        }

        # Handle specific month mentions like "during June"
        month_match = re.search(r'during\s+(\w+)', text)
        if month_match:
            month_name = month_match.group(1)
            month = self._get_month_number(month_name)
            if month:
                start_date, end_date = self._get_month_range(self.reference_date.year, month)
                return {
                    "type": "date_range",
                    "date_type": "specific_month",
                    "original_text": month_match.group(0),
                    "month": month_name,
                    **DateRange(start_date, end_date).to_dict()
                }

        return None

    def _parse_quarters(self, text: str) -> Optional[Dict]:
        """Parse quarter mentions like 'first quarter of this year', 'last quarter'."""

        for pattern, quarter in self.quarter_patterns.items():
            match = re.search(pattern + r'(?:\s+of\s+this\s+year)?', text)
            if match:
                if quarter == 'current':
                    start_date, end_date = self._get_current_quarter_range()
                elif quarter == 'last':
                    start_date, end_date = self._get_last_quarter_range()
                else:
                    start_date, end_date = self._get_quarter_range(self.reference_date.year, quarter)

                return {
                    "type": "date_range",
                    "date_type": "quarter",
                    "original_text": match.group(0),
                    "quarter": quarter,
                    **DateRange(start_date, end_date).to_dict()
                }

        return None

    def _parse_ordinal_expressions(self, text: str) -> Optional[Dict]:
        """Parse complex ordinal expressions."""

        # "second Friday of last month"
        match = re.search(r'second\s+(\w+)\s+of\s+last\s+month', text)
        if match:
            weekday = match.group(1)
            date = self._get_nth_weekday_of_month(weekday, 2, -1)  # -1 for last month
            if date:
                return {
                    "type": "single_date",
                    "date_type": "ordinal",
                    "original_text": match.group(0),
                    **SingleDate(date).to_dict()
                }

        # "last day of the previous quarter" - should return single date, not range
        match = re.search(r'(?:on\s+the\s+)?last\s+day\s+of\s+the\s+previous\s+quarter', text)
        if match:
            _, end_date = self._get_last_quarter_range()
            return {
                "type": "single_date",
                "date_type": "ordinal",
                "original_text": match.group(0),
                **SingleDate(end_date.replace(hour=0, minute=0, second=0, microsecond=0)).to_dict()
            }

        # "10th of last month" or "on the 10th of last month"
        match = re.search(r'(?:on\s+the\s+)?(\d{1,2})(st|nd|rd|th)?\s+of\s+last\s+month', text)
        if match:
            day = int(match.group(1))
            # Calculate last month
            last_month_date = self._subtract_months(self.reference_date, 1)
            try:
                specific_date = datetime(last_month_date.year, last_month_date.month, day)
                return {
                    "type": "single_date",
                    "date_type": "specific",
                    "original_text": match.group(0),
                    **SingleDate(specific_date).to_dict()
                }
            except ValueError:
                pass

        # "last month 10th" or "last month the 10th"
        match = re.search(r'last\s+month\s+(?:the\s+)?(\d{1,2})(st|nd|rd|th)?', text)
        if match:
            day = int(match.group(1))
            # Calculate last month
            last_month_date = self._subtract_months(self.reference_date, 1)
            try:
                specific_date = datetime(last_month_date.year, last_month_date.month, day)
                return {
                    "type": "single_date",
                    "date_type": "specific",
                    "original_text": match.group(0),
                    **SingleDate(specific_date).to_dict()
                }
            except ValueError:
                pass

        return None

    def _calculate_relative_range(self, amount: int, unit: str, direction: str) -> Tuple[datetime, datetime]:
        """Calculate start and end dates for relative ranges."""

        end_date = self.reference_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        if unit == 'days':
            start_date = self.reference_date - timedelta(days=amount)
        elif unit == 'weeks':
            start_date = self.reference_date - timedelta(weeks=amount)
        elif unit == 'months':
            start_date = self._subtract_months(self.reference_date, amount)
        elif unit == 'years':
            start_date = self.reference_date.replace(year=self.reference_date.year - amount)
        else:
            start_date = self.reference_date

        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        return start_date, end_date

    def _subtract_months(self, date: datetime, months: int) -> datetime:
        """Subtract months from a date, handling year boundaries."""
        month = date.month - months
        year = date.year

        while month <= 0:
            month += 12
            year -= 1

        # Handle day overflow (e.g., Jan 31 - 1 month should be Dec 31, not Dec 30)
        try:
            return date.replace(year=year, month=month)
        except ValueError:
            # Day doesn't exist in target month, use last day of month
            last_day = calendar.monthrange(year, month)[1]
            return date.replace(year=year, month=month, day=last_day)

    def _get_month_number(self, month_name: str) -> Optional[int]:
        """Get month number from month name."""
        month_name_lower = month_name.lower()
        for pattern, month_num in self.month_patterns.items():
            if re.match(pattern, month_name_lower):
                return month_num
        return None

    def _get_last_weekday(self, weekday: str) -> Optional[datetime]:
        """Get the last occurrence of a specific weekday."""
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }

        target_weekday = weekdays.get(weekday.lower())
        if target_weekday is None:
            return None

        current_weekday = self.reference_date.weekday()
        days_back = (current_weekday - target_weekday) % 7
        if days_back == 0:
            days_back = 7  # Get last week's occurrence

        last_weekday_date = self.reference_date - timedelta(days=days_back)
        return last_weekday_date.replace(hour=0, minute=0, second=0, microsecond=0)

    def _get_last_month_range(self) -> Tuple[datetime, datetime]:
        """Get the date range for last month."""
        if self.reference_date.month == 1:
            last_month = 12
            last_year = self.reference_date.year - 1
        else:
            last_month = self.reference_date.month - 1
            last_year = self.reference_date.year

        start_date = datetime(last_year, last_month, 1)
        last_day = calendar.monthrange(last_year, last_month)[1]
        end_date = datetime(last_year, last_month, last_day, 23, 59, 59, 999999)

        return start_date, end_date

    def _get_last_week_range(self) -> Tuple[datetime, datetime]:
        """Get the date range for last week (Monday to Sunday)."""
        current_weekday = self.reference_date.weekday()
        last_monday = self.reference_date - timedelta(days=current_weekday + 7)
        last_sunday = last_monday + timedelta(days=6)

        start_date = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = last_sunday.replace(hour=23, minute=59, second=59, microsecond=999999)

        return start_date, end_date

    def _get_last_year_range(self) -> Tuple[datetime, datetime]:
        """Get the date range for last year."""
        last_year = self.reference_date.year - 1
        start_date = datetime(last_year, 1, 1)
        end_date = datetime(last_year, 12, 31, 23, 59, 59, 999999)

        return start_date, end_date

    def _get_month_range(self, year: int, month: int) -> Tuple[datetime, datetime]:
        """Get the date range for a specific month and year."""
        start_date = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59, 999999)

        return start_date, end_date

    def _get_current_quarter_range(self) -> Tuple[datetime, datetime]:
        """Get the date range for the current quarter."""
        current_month = self.reference_date.month
        quarter = (current_month - 1) // 3 + 1
        return self._get_quarter_range(self.reference_date.year, f'Q{quarter}')

    def _get_last_quarter_range(self) -> Tuple[datetime, datetime]:
        """Get the date range for the last quarter."""
        current_month = self.reference_date.month
        current_quarter = (current_month - 1) // 3 + 1

        if current_quarter == 1:
            last_quarter = 4
            year = self.reference_date.year - 1
        else:
            last_quarter = current_quarter - 1
            year = self.reference_date.year

        return self._get_quarter_range(year, f'Q{last_quarter}')

    def _get_quarter_range(self, year: int, quarter: str) -> Tuple[datetime, datetime]:
        """Get the date range for a specific quarter."""
        quarter_months = {
            'Q1': (1, 3), 'Q2': (4, 6), 'Q3': (7, 9), 'Q4': (10, 12)
        }

        start_month, end_month = quarter_months[quarter]
        start_date = datetime(year, start_month, 1)
        last_day = calendar.monthrange(year, end_month)[1]
        end_date = datetime(year, end_month, last_day, 23, 59, 59, 999999)

        return start_date, end_date

    def _get_nth_weekday_of_month(self, weekday: str, nth: int, month_offset: int = 0) -> Optional[datetime]:
        """Get the nth occurrence of a weekday in a specific month."""
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }

        target_weekday = weekdays.get(weekday.lower())
        if target_weekday is None:
            return None

        # Calculate target month
        target_month = self.reference_date.month + month_offset
        target_year = self.reference_date.year

        while target_month <= 0:
            target_month += 12
            target_year -= 1
        while target_month > 12:
            target_month -= 12
            target_year += 1

        # Find the first occurrence of the weekday in the month
        first_day = datetime(target_year, target_month, 1)
        first_weekday = first_day.weekday()

        days_to_add = (target_weekday - first_weekday) % 7
        first_occurrence = first_day + timedelta(days=days_to_add)

        # Calculate the nth occurrence
        nth_occurrence = first_occurrence + timedelta(weeks=nth - 1)

        # Verify it's still in the same month
        if nth_occurrence.month == target_month:
            return nth_occurrence

        return None


def interactive_date_parser():
    """Interactive command-line interface for the date parser."""

    print("=" * 60)
    print("Complex Date Parsing System")
    print("=" * 60)
    print("Enter medical query strings to extract date information.")
    print("Type 'quit' or 'exit' to stop.")
    print("Type 'test' to run with sample strings from strings.txt")
    print("=" * 60)

    parser = ComplexDateParser()

    while True:
        try:
            user_input = input("\nEnter query: ").strip()

            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            if user_input.lower() == 'test':
                test_with_sample_strings(parser)
                continue

            if not user_input:
                print("Please enter a query.")
                continue

            result = parser.parse_date_expression(user_input)
            print("\nExtracted Date Information:")
            print(json.dumps(result, indent=2))

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def test_with_sample_strings(parser: ComplexDateParser):
    """Test the parser with sample strings from strings.txt."""

    try:
        with open('strings.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract strings (remove quotes and split by lines)
        strings = []
        for line in content.split('\n'):
            line = line.strip()
            if line and line.startswith('"') and line.endswith('"'):
                strings.append(line[1:-1])  # Remove quotes

        print(f"\nTesting with {len(strings)} sample strings...\n")

        for i, query in enumerate(strings[:10]):  # Test first 10 for brevity
            print(f"Query {i+1}: {query}")
            result = parser.parse_date_expression(query)
            print(f"Result: {json.dumps(result, indent=2)}")
            print("-" * 50)

        print(f"\nShowing first 10 of {len(strings)} total strings.")
        print("Use individual queries for detailed analysis.")

    except FileNotFoundError:
        print("strings.txt file not found in current directory.")
    except Exception as e:
        print(f"Error reading strings.txt: {e}")


if __name__ == "__main__":
    interactive_date_parser()
