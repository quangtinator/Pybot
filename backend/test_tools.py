from src.tools import SetupMockBookingTool, CurrentTimeTool, DocumentTool

def test_booking_tool_string_sanitization():
    """
    Tests PURE CODE: String manipulation.
    Verifies that the tool correctly strips whitespace and handles weird capitalization 
    using the .lower().strip() logic written in the code.
    """
    tool = SetupMockBookingTool()
    
    # Passing messy input
    result = tool.execute("   tOkYo  \n")
    
    assert "Flight JL001" in result
    assert "On Time" in result

def test_current_time_tool_exception_handling():
    """
    Tests PURE CODE: Try/Except blocks.
    Verifies that passing a mathematically invalid timezone string triggers 
    the Except block rather than crashing the Python server with a traceback.
    """
    tool = CurrentTimeTool()
    
    # "Mars/City" is not a valid pytz timezone
    result = tool.execute("Mars/City")
    assert "Could not determine time for timezone" in result
    assert "Mars/City" in result
