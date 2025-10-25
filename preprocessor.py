import re
import pandas as pd

def preprocess(data):
    # Regex patterns updated for case-insensitive AM/PM and slightly flexible spacing
    # Format 1: Android-style (24-hr) e.g., 10/20/20, 14:30 - User: Message
    pat1 = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s*-\s*([\w\W]+?):\s*([\w\W]+)'
    # Format 2: Android-style (12-hr) e.g., 10/10/20, 12:00 AM - User: Message
    pat2 = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}\s*[APap][Mm])\s*-\s*([\w\W]+?):\s*([\w\W]+)'
    # Format 3: iOS-style (24-hr) e.g., [10/20/20, 14:30:05] User: Message
    pat3 = r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2})\]\s*([\w\W]+?):\s*([\w\W]+)'
    # Format 4: iOS-style (12-hr) e.g., [10/10/20, 12:00:05 AM] User: Message
    pat4 = r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}\s*[APap][Mm])\]\s*([\w\W]+?):\s*([\w\W]+)'

    # Patterns for system messages (no "User: " part) - updated AM/PM
    pat5 = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s*-\s*([\w\W]+)'
    pat6 = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}\s*[APap][Mm])\s*-\s*([\w\W]+)'
    pat7 = r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2})\]\s*([\w\W]+)'
    pat8 = r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}:\d{2}\s*[APap][Mm])\]\s*([\w\W]+)'

    patterns = [pat1, pat2, pat3, pat4, pat5, pat6, pat7, pat8]

    parsed_data = []
    message_buffer = []

    # --- Enhanced Cleaning ---
    # Remove common zero-width space characters and others that might interfere
    invisible_chars = ['\u200e', '\u200f', '\u202a', '\u202b', '\u202c', '\u202d', '\u202e', '\ufeff']
    cleaned_data = data
    for char in invisible_chars:
        cleaned_data = cleaned_data.replace(char, '')

    for line_raw in cleaned_data.split('\n'):
        line = line_raw.strip() # Strip leading/trailing whitespace
        if not line:
             continue

        matched = False
        for i, pattern in enumerate(patterns):
            match = re.match(pattern, line)
            if match:
                if message_buffer:
                    processed_buffer = [item.strip() for item in message_buffer]
                    parsed_data.append(processed_buffer)

                if i < 4: # User message
                    date, time, user, message = match.groups()
                else: # System message
                    date, time, message = match.groups()
                    user = 'group_notification'

                message_buffer = [date, time, user, message]
                matched = True
                break

        if not matched and message_buffer:
            # Append the original raw line (but stripped) if it's a continuation
            message_buffer[3] += '\n' + line

    if message_buffer:
        processed_buffer = [item.strip() for item in message_buffer]
        parsed_data.append(processed_buffer)

    if not parsed_data:
        # Give a more specific error if the initial regex matching failed completely
        raise ValueError("Could not find any recognizable message lines. Please ensure the file is a standard WhatsApp chat export and not corrupted.")

    df = pd.DataFrame(parsed_data, columns=['date_str', 'time_str', 'user', 'message'])

    # --- Date and Time Parsing (Keep the flexible approach) ---
    df['datetime_str'] = df['date_str'] + ' ' + df['time_str']

    parsed_dates = None
    common_formats = [
        # Add formats with different separators or orders if needed, but rely on dayfirst toggle first
        "%m/%d/%y %I:%M %p", "%m/%d/%Y %I:%M %p", # MM/DD/YY H:MM AM/PM (Common US-style 12hr)
        "%d/%m/%y %I:%M %p", "%d/%m/%Y %I:%M %p", # DD/MM/YY H:MM AM/PM
        "%m/%d/%y %H:%M",    "%m/%d/%Y %H:%M",    # MM/DD/YY HH:MM (US-style 24hr)
        "%d/%m/%y %H:%M",    "%d/%m/%Y %H:%M",    # DD/MM/YY HH:MM
        # iOS formats (including seconds)
        "%m/%d/%y %I:%M:%S %p", "%m/%d/%Y %I:%M:%S %p",
        "%d/%m/%y %I:%M:%S %p", "%d/%m/%Y %I:%M:%S %p",
        "%m/%d/%y %H:%M:%S",    "%m/%d/%Y %H:%M:%S",
        "%d/%m/%y %H:%M:%S",    "%d/%m/%Y %H:%M:%S",
    ]

    # Try inferring first (often works for simple cases)
    try:
        parsed_dates = pd.to_datetime(df['datetime_str'], infer_datetime_format=True)
    except Exception: # Broad exception to catch various parsing issues
        # Try specific formats if inference fails
        for fmt in common_formats:
            try:
                parsed_dates = pd.to_datetime(df['datetime_str'], format=fmt)
                break
            except ValueError:
                continue

        # If specific formats failed, try toggling dayfirst
        if parsed_dates is None:
            try:
                parsed_dates = pd.to_datetime(df['datetime_str'], dayfirst=True, infer_datetime_format=True)
            except Exception:
                try:
                    parsed_dates = pd.to_datetime(df['datetime_str'], dayfirst=False, infer_datetime_format=True)
                except Exception:
                    # If absolutely everything fails
                     raise ValueError("Failed to parse date/time strings even after trying multiple formats. The date format might be highly non-standard.")

    df['date'] = parsed_dates
    df.drop(columns=['date_str', 'time_str', 'datetime_str'], inplace=True)

    # --- Feature Engineering ---
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create time periods for the heatmap
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour:02d}-{(hour + 1):02d}")
    df['period'] = period

    return df