import asyncio
import json
import os
from datetime import date
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class UnifiedDateTimeTestSuite:
    def __init__(self):
        self.current_date = date(2025, 7, 19)
        self.test_cases = self.define_test_cases()
        self.results = []
    
    def define_test_cases(self):
        """Define all test cases with expected results"""
        return [
            # Category 1: TODAY queries (should be single_date)
            {
                "query": "today",
                "expected_type": "single_date",
                "expected_date": "2025-07-19",
                "description": "Basic today query"
            },
            {
                "query": "what day is it today?",
                "expected_type": "single_date",
                "expected_date": "2025-07-19",
                "description": "Today as question"
            },
            {
                "query": "get me all cases that came in today",
                "expected_type": "single_date",
                "expected_date": "2025-07-19",
                "description": "Cases today query"
            },
            {
                "query": "what happened today",
                "expected_type": "single_date",
                "expected_date": "2025-07-19",
                "description": "Events today query"
            },
            
            # Category 2: YESTERDAY and relative days (should be single_date)
            {
                "query": "yesterday",
                "expected_type": "single_date",
                "expected_date": "2025-07-18",
                "description": "Basic yesterday"
            },
            {
                "query": "get me cases from yesterday",
                "expected_type": "single_date",
                "expected_date": "2025-07-18",
                "description": "Yesterday with context"
            },
            {
                "query": "3 days ago",
                "expected_type": "single_date",
                "expected_date": "2025-07-16",
                "description": "Basic 3 days ago"
            },
            {
                "query": "get me cases from 3 days ago",
                "expected_type": "single_date", 
                "expected_date": "2025-07-16",
                "description": "3 days ago with context"
            },
            {
                "query": "2 weeks ago",
                "expected_type": "single_date",
                "expected_date": "2025-07-05",
                "description": "Basic 2 weeks ago"
            },
            {
                "query": "get me cases from 2 weeks ago",
                "expected_type": "single_date",
                "expected_date": "2025-07-05", 
                "description": "2 weeks ago with context"
            },
            {
                "query": "1 month ago",
                "expected_type": "single_date",
                "expected_date": "2025-06-19",
                "description": "Basic 1 month ago"
            },
            {
                "query": "get me cases from 1 month ago",
                "expected_type": "single_date",
                "expected_date": "2025-06-19",
                "description": "1 month ago with context"
            },
            
            # Category 3: WEEKDAY queries (should be single_date)
            {
                "query": "last Monday",
                "expected_type": "single_date",
                "expected_date": "2025-07-14",
                "description": "Basic last Monday"
            },
            {
                "query": "get me cases from last monday",
                "expected_type": "single_date", 
                "expected_date": "2025-07-14",
                "description": "Last Monday with context"
            },
            {
                "query": "last Thursday",
                "expected_type": "single_date",
                "expected_date": "2025-07-17",
                "description": "Basic last Thursday"
            },
            {
                "query": "get me cases from last thursday",
                "expected_type": "single_date",
                "expected_date": "2025-07-17",
                "description": "Last Thursday with context"
            },
            {
                "query": "last Friday",
                "expected_type": "single_date",
                "expected_date": "2025-07-18",
                "description": "Last Friday"
            },
            
            # Category 4: Specific days of month
            {
                "query": "get me cases from 3rd of this month",
                "expected_type": "single_date",
                "expected_date": "2025-07-03",
                "description": "3rd of this month"
            },
            {
                "query": "get me cases from 15th of last month",
                "expected_type": "single_date",
                "expected_date": "2025-06-15", 
                "description": "15th of last month"
            },
            {
                "query": "get me cases from 1st of next month",
                "expected_type": "single_date",
                "expected_date": "2025-08-01",
                "description": "1st of next month"
            },
            
            # Category 5: WEEK RANGES (should be date_range)
            {
                "query": "this week",
                "expected_type": "date_range",
                "expected_start": "2025-07-14",
                "expected_end": "2025-07-20",
                "description": "Basic this week range"
            },
            {
                "query": "get me cases from this week",
                "expected_type": "date_range",
                "expected_start": "2025-07-14",
                "expected_end": "2025-07-20",
                "description": "This week with context"
            },
            {
                "query": "last week",
                "expected_type": "date_range",
                "expected_start": "2025-07-07",
                "expected_end": "2025-07-13",
                "description": "Basic last week range"
            },
            {
                "query": "get me cases from last week",
                "expected_type": "date_range",
                "expected_start": "2025-07-07",
                "expected_end": "2025-07-13", 
                "description": "Last week with context"
            },
            {
                "query": "show me this week's data",
                "expected_type": "date_range",
                "expected_start": "2025-07-14",
                "expected_end": "2025-07-20",
                "description": "This week's data"
            },
            
            # Category 6: MONTH RANGES (should be date_range)
            {
                "query": "this month",
                "expected_type": "date_range",
                "expected_start": "2025-07-01",
                "expected_end": "2025-07-31",
                "description": "Basic this month range"
            },
            {
                "query": "last month",
                "expected_type": "date_range",
                "expected_start": "2025-06-01",
                "expected_end": "2025-06-30",
                "description": "Basic last month range"
            },
            {
                "query": "get me cases from last month",
                "expected_type": "date_range",
                "expected_start": "2025-06-01",
                "expected_end": "2025-06-30",
                "description": "Last month with context"
            },
            {
                "query": "feb",
                "expected_type": "date_range",
                "expected_start": "2025-02-01",
                "expected_end": "2025-02-28",
                "description": "Basic February range"
            },
            {
                "query": "get me cases from feb",
                "expected_type": "date_range", 
                "expected_start": "2025-02-01",
                "expected_end": "2025-02-28",
                "description": "February with context"
            },
            {
                "query": "get me cases from march last year",
                "expected_type": "date_range",
                "expected_start": "2024-03-01", 
                "expected_end": "2024-03-31",
                "description": "March last year"
            },
            
            # Category 7: Multi-month ranges
            {
                "query": "get me cases from march and april this year",
                "expected_type": "date_range",
                "expected_start": "2025-03-01",
                "expected_end": "2025-04-30",
                "description": "March and April this year"
            },
            {
                "query": "get me cases from jan to march this year", 
                "expected_type": "date_range",
                "expected_start": "2025-01-01",
                "expected_end": "2025-03-31",
                "description": "January to March this year"
            },
            {
                "query": "get me cases from march to august last year",
                "expected_type": "date_range",
                "expected_start": "2024-03-01",
                "expected_end": "2024-08-31", 
                "description": "March to August last year"
            },
            
            # Category 8: Edge cases
            {
                "query": "cases from today",
                "expected_type": "single_date",
                "expected_date": "2025-07-19",
                "description": "Cases from today"
            }
        ]
    
    async def run_test_case(self, session, test_case):
        """Run a single test case"""
        try:
            # Import the process_query function from client
            from client import process_query
            
            print(f"\n🧪 Testing: {test_case['description']}")
            print(f"   Query: '{test_case['query']}'")
            
            # Process the query
            result = await process_query(session, test_case['query'])
            
            # Check result type
            actual_type = result.get('type')
            expected_type = test_case['expected_type']
            
            if actual_type != expected_type:
                print(f"   ❌ FAIL - Type mismatch: expected {expected_type}, got {actual_type}")
                return {
                    'test': test_case['description'],
                    'query': test_case['query'],
                    'status': 'FAIL',
                    'error': f"Type mismatch: expected {expected_type}, got {actual_type}",
                    'expected': test_case,
                    'actual': result
                }
            
            # Check dates based on type
            if expected_type == 'single_date':
                actual_date = result.get('date')
                expected_date = test_case['expected_date']
                
                if actual_date != expected_date:
                    print(f"   ❌ FAIL - Date mismatch: expected {expected_date}, got {actual_date}")
                    return {
                        'test': test_case['description'],
                        'query': test_case['query'], 
                        'status': 'FAIL',
                        'error': f"Date mismatch: expected {expected_date}, got {actual_date}",
                        'expected': test_case,
                        'actual': result
                    }
            
            elif expected_type == 'date_range':
                actual_start = result.get('start_date')
                actual_end = result.get('end_date')
                expected_start = test_case['expected_start']
                expected_end = test_case['expected_end']
                
                if actual_start != expected_start or actual_end != expected_end:
                    print(f"   ❌ FAIL - Range mismatch: expected {expected_start} to {expected_end}, got {actual_start} to {actual_end}")
                    return {
                        'test': test_case['description'],
                        'query': test_case['query'],
                        'status': 'FAIL', 
                        'error': f"Range mismatch: expected {expected_start} to {expected_end}, got {actual_start} to {actual_end}",
                        'expected': test_case,
                        'actual': result
                    }
            
            # Test passed
            print(f"   ✅ PASS")
            return {
                'test': test_case['description'],
                'query': test_case['query'],
                'status': 'PASS',
                'expected': test_case,
                'actual': result
            }
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            return {
                'test': test_case['description'], 
                'query': test_case['query'],
                'status': 'ERROR',
                'error': str(e),
                'expected': test_case,
                'actual': None
            }
    
    async def run_all_tests(self):
        """Run all test cases"""
        print("🚀 Starting Unified Comprehensive DateTime Tests")
        print(f"📅 Test Date: {self.current_date}")
        print("=" * 60)
        
        server_params = StdioServerParameters(
            command="python", args=["server.py"], cwd=os.path.dirname(__file__)
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                for test_case in self.test_cases:
                    result = await self.run_test_case(session, test_case)
                    self.results.append(result)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        failed = len([r for r in self.results if r['status'] == 'FAIL'])
        errors = len([r for r in self.results if r['status'] == 'ERROR'])
        total = len(self.results)
        
        print(f"✅ PASSED: {passed}/{total}")
        print(f"❌ FAILED: {failed}/{total}")
        print(f"🔥 ERRORS: {errors}/{total}")
        print(f"📈 SUCCESS RATE: {(passed/total)*100:.1f}%")
        
        # Print failed tests
        if failed > 0 or errors > 0:
            print("\n🔍 FAILED/ERROR TESTS:")
            print("-" * 40)
            for result in self.results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"\n❌ {result['test']}")
                    print(f"   Query: '{result['query']}'")
                    print(f"   Error: {result['error']}")
                    if result.get('actual'):
                        print(f"   Actual: {json.dumps(result['actual'], indent=4)}")
        
        # Print all results in detail
        print(f"\n📋 DETAILED RESULTS:")
        print("-" * 40)
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")

    def run_specific_categories(self, categories):
        """Filter and run only specific categories of tests
        
        Args:
            categories (list): List of category numbers to run
        """
        # Implementation for future enhancement
        pass

async def main():
    """Run the comprehensive test suite"""
    test_suite = UnifiedDateTimeTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
