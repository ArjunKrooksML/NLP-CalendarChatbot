import datetime
from dateutil import parser
from tzlocal import get_localzone


def parse_dt(ext_details):
    """Parse date and time from string."""
    if not ext_details or not ext_details.get('date') or not ext_details.get('start_time'):
        print("Missing date or start time from extracted details.")
        return None, None
    
    start_dt = None
    end_dt = None
    date_str = ext_details['date']
    start_time_str = ext_details['start_time']
    end_time_str = ext_details.get('end_time')

    try:
        start_str_combined = f"{date_str} {start_time_str}"
        start_dt = parser.parse(start_str_combined)
        print(f"Parsed start datetime: {start_dt}")

        if end_time_str:
            try:
                end_time_parsed = parser.parse(end_time_str, default=start_dt.replace(hour=0, minute=0, second=0, microsecond=0))
                end_dt = start_dt.replace(hour=end_time_parsed.hour, minute=end_time_parsed.minute, second=end_time_parsed.second, microsecond=end_time_parsed.microsecond)
                if end_dt < start_dt:
                    print(f"Parsed end time '{end_dt}' is earlier than start time '{start_dt}'.")
                    end_dt += datetime.timedelta(days=1)
                elif end_dt == start_dt:
                    print(f"Parsed end time '{end_dt}' is the same as start time '{start_dt}'.")
                    end_dt = start_dt + datetime.timedelta(hours=1)

            except (parser.ParserError, TypeError, ValueError) as e:
                 print(f"Could not parse end time string '{end_time_str}' ({e}).")
                 end_dt = start_dt + datetime.timedelta(hours=1)

        else:
            print("End time not specified by LLM.")
            end_dt = start_dt + datetime.timedelta(hours=1)        


        print(f"Parsed end datetime: {end_dt}")
        return start_dt, end_dt

    except (parser.ParserError, OverflowError, ValueError, TypeError) as e: 
        print(f"Error parsing date/time string: {e}")
        print(f"Attempted to parse start: '{date_str} {start_time_str}'")
        if end_time_str:
            print(f"Attempted to parse end: '{end_time_str}' relative to start date")
        return None, None
    except Exception as e: 
         print(f"An unexpected error occurred during date/time parsing: {e}")
         return None, None                 

