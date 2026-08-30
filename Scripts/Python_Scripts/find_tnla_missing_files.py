import os
import re

def find_missing_in_directory(directory_path):
    # Pattern to match the prefix 'ac', 6 digits, and the extension
    pattern = re.compile(r"ac(\d{6})\.(csv|json)")
    
    # Get all files in the directory
    try:
        files = os.listdir(directory_path)
    except FileNotFoundError:
        return "Directory not found."

    # Extract all unique numbers found in the filenames
    found_numbers = set()
    for f in files:
        match = pattern.search(f)
        if match:
            found_numbers.add(int(match.group(1)))
    
    if not found_numbers:
        return "No matching files found in the directory."

    # Determine the range to check
    start_num = min(found_numbers)
    end_num = max(found_numbers)
    
    missing_report = []

    # Check every number in the range for both .csv and .json
    for num in range(start_num, end_num + 1):
        formatted_id = f"{num:06d}"
        for ext in ['csv', 'json']:
            filename = f"ac{formatted_id}.{ext}"
            if filename not in files:
                missing_report.append(filename)
                
    return missing_report

# Usage: Replace '.' with your actual folder path
missing_files = find_missing_in_directory('.')

print(f"Scanned sequence from {min(missing_files) if missing_files else 'N/A'} upwards.")
print(f"Total missing files found: {len(missing_files)}")
for file in missing_files:
    print(f"MISSING: {file}")