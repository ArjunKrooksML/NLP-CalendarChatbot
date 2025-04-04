import config
import sys
from tzlocal import get_localzone
import config 
from calendar_conn import auth_cal, createcalendarevent
from llm_util import llm_ini, extract_llm
from dt import parse_dt

def display(event_data):
    """Prints the event details for user confirmation."""
    print("\nOkay, I understood the following event details:")
    print(f"- Title: {event_data['title']}")
    try:
        local_tz = get_localzone()
        tz_name = str(local_tz)
    except Exception:
        tz_name = "Local Timezone" # Fallback

    
    try:
        start_str = event_data['start_dt'].strftime('%A, %B %d, %Y at %I:%M %p')
        end_str = event_data['end_dt'].strftime('%A, %B %d, %Y at %I:%M %p')
        print(f"- Start: {start_str} ({tz_name})")
        print(f"- End:   {end_str} ({tz_name})")
    except AttributeError:
         print("- Start: [Error formatting start date/time]")
         print("- End:   [Error formatting end date/time]")
         return False # Indicate formatting error

    return True


def run_chatbot():
    """Runs the main chatbot interaction loop."""
    print("Initializing Calendar Chatbot...")

    
    gcalendar_service = auth_cal()
    if not gcalendar_service:
        print("\nFailed to authenticate Google Calendar API. Please check credentials. Exiting.")
        sys.exit(1) 

    
    if not llm_ini():
        print("\nFailed to initialize LLM. Please check model name, resources, and dependencies. Exiting.")
        sys.exit(1) 

    print("\n--- Welcome to the Scheduling Chatbot! ---")
    print("You can ask me to schedule meetings, appointments, etc.")
    print("Example: 'Schedule a team meeting next Tuesday from 3 PM to 4 PM'")
    print("Type 'quit' or 'exit' to stop.")

    while True:
        try:
            user_input = input("\n> ")
        except EOFError: # Handle Ctrl+D
             print("\nExiting...")
             break
        except KeyboardInterrupt: # Handle Ctrl+C
             print("\nExiting...")
             break


        if user_input.lower().strip() in ['quit', 'exit', 'bye', 'q']:
            break

        if not user_input.strip():
            continue

        #Extract details using LLM
        extracted_info = extract_llm(user_input)

        # Verifies the LLM ini and data transmission
        if not extracted_info or not extracted_info.get('title') or not extracted_info.get('date') or not extracted_info.get('start_time'):
            if extracted_info and any(v for k, v in extracted_info.items() if k in ['title', 'date', 'start_time', 'end_time']): # Check if *any* key info was partially extracted
                print("\nI understood some details:")
                for key, value in extracted_info.items():
                    if value:
                        print(f"- {key.replace('_', ' ').title()}: {value}")
                print("\nbut the key information (like title, full date, or start time) is missing")
            else:
                 print("\nSorry, I couldn't understand the scheduling details from that.")

            print("Could you please rephrase or provide more specific info?")
            continue 

        #Parsing Dates and Times
        start_datetime, end_datetime = parse_dt(extracted_info)

        if not start_datetime or not end_datetime:
            print("\nSorry, could not parse date and time from the given info")
            print(f"  Date='{extracted_info.get('date')}', Start='{extracted_info.get('start_time')}', End='{extracted_info.get('end_time')}'")
            print("Could you please write the date and time more clearly in a JSON Datetime format?")
            continue # Asks for our input again

        # Store all data for confirmation and creation
        event_data_for_confirmation = {
            'title': extracted_info.get('title'),
            'date_str': extracted_info.get('date'),
            'start_time_str': extracted_info.get('start_time'),
            'end_time_str': extracted_info.get('end_time'),
            'start_dt': start_datetime,
            'end_dt': end_datetime
        }

        #Confirms with the User
        if not display(event_data_for_confirmation):
             print("Eroor displaying the parsed dates, Please try rephrasing.")
             continue

        while True:
            try:
                confirm = input("\nShall I schedule this event in your Google Calendar? (yes/no): ").lower().strip()
            except EOFError:
                 print("\nExiting...")
                 return # Exit function cleanly
            except KeyboardInterrupt:
                 print("\nOperation cancelled.")
                 break # Break confirmation loop, go back to asking for input

            if confirm in ['yes', 'y']:
                #Creates a Google Calendar Event linked to your Acc
                print("Proceeding with event creation...")
                success = createcalendarevent(gcalendar_service, event_data_for_confirmation)
                # No need for further prints here, create_google_calendar_event handles success/failure messages
                break # Exit confirmation loop
            elif confirm in ['no', 'n']:
                print("Okay, I won't schedule this event. Please provide the correct details or a new request.")
                break # Exit confirmation loop
            else:
                print("Please answer y/n.")

    print("\nGoodbye!")

if __name__ == '__main__':
    run_chatbot()