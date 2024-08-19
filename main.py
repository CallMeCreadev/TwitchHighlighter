import json
from datetime import datetime
from collections import defaultdict
import re
from dateutil import parser

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    return data

def extract_messages_and_timestamps(comment_data):
    messages = []
    for item in comment_data:
        if isinstance(item, dict):
            timestamp = item.get('created_at')
            message = item.get('message', {}).get('body', '')
            messages.append((timestamp, message))
    return messages

def count_patterns_per_15_seconds(messages, patterns):
    counts = defaultdict(int)
    pattern_res = [re.compile(pattern) for pattern in patterns]

    for timestamp, message in messages:
        try:
            # Use dateutil.parser to handle various datetime formats
            dt = parser.isoparse(timestamp)
            quarter_minute = dt.replace(second=(dt.second // 15) * 15, microsecond=0)
        except (ValueError, TypeError) as e:
            print(f"Error parsing timestamp {timestamp}: {e}")
            continue

        # Count occurrences of each pattern in the message
        for pattern_re in pattern_res:
            count = len(pattern_re.findall(message))
            counts[quarter_minute] += count

    return counts

def convert_timestamps_to_sequential(counts):
    all_times = sorted(counts.keys())
    time_mapping = {time: idx for idx, time in enumerate(all_times)}

    sequential_counts = defaultdict(int)
    for time, count in counts.items():
        sequential_time = time_mapping[time]
        sequential_counts[sequential_time] += count

    return sequential_counts, len(all_times)

def format_seconds(seconds):
    hours = seconds // 3600
    remaining_seconds = seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    return f"{hours}:{minutes:02}:{seconds:02}"

def main():
    file_path = 'chat_messages.json'  # Update with your JSON file path
    patterns = [r'\bLUL\b', r'\bKEKW\b', r'\bOMEGALUL\b']  # Update with the patterns you want to count

    data = load_json(file_path)
    if data is None:
        print("Failed to load JSON data.")
        return

    comment_data = data.get('comments', [])
    messages = extract_messages_and_timestamps(comment_data)
    pattern_counts = count_patterns_per_15_seconds(messages, patterns)
    sequential_counts, total_intervals = convert_timestamps_to_sequential(pattern_counts)

    sorted_counts = sorted(sequential_counts.items(), key=lambda x: x[1], reverse=True)
    top_8 = sorted_counts[:8]

    for interval, count in top_8:
        formatted_time = format_seconds(interval * 15)
        print(f"Time {formatted_time}: {count}")

    # Print the hour/minute/second of the final timestamp
    final_formatted_time = format_seconds((total_intervals - 1) * 15)
    print(f"Final timestamp: {final_formatted_time}")

if __name__ == "__main__":
    main()
