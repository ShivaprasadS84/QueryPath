import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import logging

from date_calculator import get_single_date, get_date_range, get_month_range, get_current_date, get_week_range

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("datetime-server")

# Create server instance
server = Server("datetime-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available datetime tools"""
    return [
        Tool(
            name="get_current_date",
            description="Get the current date",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_single_date",
            description="Calculate a single date based on reference point and offset",
            inputSchema={
                "type": "object",
                "properties": {
                    "reference_point": {
                        "type": "string",
                        "enum": ["today", "start_of_week", "start_of_month", "start_of_year", "specific_month", "specific_weekday", "specific_day_of_month"],
                        "description": "Reference point for calculation"
                    },
                    "offset_value": {
                        "type": "integer",
                        "description": "Numeric offset (negative for past, positive for future)"
                    },
                    "offset_unit": {
                        "type": "string",
                        "description": "Unit of offset: days, weeks, months, years, month_name, or weekday_name"
                    }
                },
                "required": ["reference_point", "offset_value", "offset_unit"]
            }
        ),
        Tool(
            name="get_date_range",
            description="Calculate a date range with start and end dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_reference": {
                        "type": "string",
                        "enum": ["today", "start_of_week", "start_of_month", "start_of_year", "specific_month", "specific_weekday", "specific_day_of_month"],
                        "description": "Start reference point"
                    },
                    "start_offset_value": {
                        "type": "integer",
                        "description": "Start offset value"
                    },
                    "start_offset_unit": {
                        "type": "string",
                        "description": "Start offset unit"
                    },
                    "end_reference": {
                        "type": "string",
                        "enum": ["today", "start_of_week", "start_of_month", "start_of_year", "specific_month", "specific_weekday", "specific_day_of_month"],
                        "description": "End reference point"
                    },
                    "end_offset_value": {
                        "type": "integer",
                        "description": "End offset value"
                    },
                    "end_offset_unit": {
                        "type": "string",
                        "description": "End offset unit"
                    }
                },
                "required": ["start_reference", "start_offset_value", "start_offset_unit", "end_reference", "end_offset_value", "end_offset_unit"]
            }
        ),
        Tool(
            name="get_month_range",
            description="Get full month range for a specific month",
            inputSchema={
                "type": "object",
                "properties": {
                    "month_name": {
                        "type": "string",
                        "description": "Name of the month (e.g., 'february', 'feb', 'march')"
                    },
                    "year_offset": {
                        "type": "integer",
                        "description": "Year offset from current year (0 = this year, -1 = last year)",
                        "default": 0
                    }
                },
                "required": ["month_name"]
            }
        ),
        Tool(
            name="get_week_range",
            description="Get week range (Monday to Sunday)",
            inputSchema={
                "type": "object",
                "properties": {
                    "week_offset": {
                        "type": "integer",
                        "description": "Week offset from current week (0 = this week, -1 = last week)",
                        "default": 0
                    }
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    try:
        if name == "get_current_date":
            result = get_current_date()
            return [TextContent(type="text", text=result)]
        
        elif name == "get_single_date":
            reference_point = arguments["reference_point"]
            offset_value = arguments["offset_value"]
            offset_unit = arguments["offset_unit"]
            
            result = get_single_date(reference_point, offset_value, offset_unit)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_date_range":
            start_reference = arguments["start_reference"]
            start_offset_value = arguments["start_offset_value"]
            start_offset_unit = arguments["start_offset_unit"]
            end_reference = arguments["end_reference"]
            end_offset_value = arguments["end_offset_value"]
            end_offset_unit = arguments["end_offset_unit"]
            
            result = get_date_range(
                start_reference, start_offset_value, start_offset_unit,
                end_reference, end_offset_value, end_offset_unit
            )
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "get_month_range":
            month_name = arguments["month_name"]
            year_offset = arguments.get("year_offset", 0)
            
            result = get_month_range(month_name, year_offset)
            return [TextContent(type="text", text=json.dumps(result))]
        
        elif name == "get_week_range":
            week_offset = arguments.get("week_offset", 0)
            
            result = get_week_range(week_offset)
            return [TextContent(type="text", text=json.dumps(result))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
