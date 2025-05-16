import json
import os

def total_merits_in_folder(folder_path, output_file):
    results = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".log"):  # Adjust if log files have a different extension
            total_merits = 0
            min_total_merits = float("inf")
            max_total_merits = float("-inf")
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r") as file:
                for line in file:
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get("event") == "PowerplayMerits":
                            merits_gained = log_entry.get("MeritsGained", 0)
                            total_merits += merits_gained
                            total_merits_value = log_entry.get("TotalMerits", 0)

                            # Track min and max within each file
                            min_total_merits = min(min_total_merits, total_merits_value)
                            max_total_merits = max(max_total_merits, total_merits_value)

                    except json.JSONDecodeError:
                        pass  # Ignore invalid JSON lines

            # Ensure min/max values are meaningful (if no PowerplayMerits events exist)
            if min_total_merits == float("inf"):
                min_total_merits = "N/A"
                max_total_merits = "N/A"
                merits_earned = "N/A"
            else:
                merits_earned = max_total_merits - min_total_merits

            result = (
                f"{filename}: Total Merits Gained = {total_merits}, "
                f"Min TotalMerits = {min_total_merits}, Max TotalMerits = {max_total_merits}, "
                f"Merits Earned = {merits_earned}"
            )
            print(result)  # Print to console
            results.append(result)  # Store for output file

    # Write results to a file in the same folder
    with open(output_file, "w") as out_file:
        out_file.write("\n".join(results))

# Run the script in the specified relative path
folder_path = os.getcwd()
output_file = os.path.join(folder_path, "results.txt")
total_merits_in_folder(folder_path, output_file)

print(f"\nResults saved to {output_file}")