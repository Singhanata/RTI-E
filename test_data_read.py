import os
import glob
import csv

def read_and_concatenate_csv_files(folder_path, prefix, delimiter=","):
    """Reads CSV files with a given prefix and concatenates column-wise into a 2D list."""
    
    # Find all CSV files matching the prefix
    file_list = sorted(glob.glob(os.path.join(folder_path, f"{prefix}*.csv")))

    # List to store data column-wise
    columns = []

    for file in file_list:
        try:
            with open(file, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=delimiter)  # Read CSV file
                
                # Read entire file, each row is converted to a list of floats
                numbers = [list(map(float, row)) for row in reader]
                    
                if not len(columns):columns = numbers
                else: columns = [row1 + row2 for row1, row2 in zip(columns, numbers)]
                # Append as a new column
                # columns.append(numbers)
                
                print(f"📄 Processed: {file}")  # Debugging message
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")

    # Handling files with different row lengths by padding with `None`
    # max_rows = max(len(col) for col in columns)  # Find max rows among all files
    # padded_columns = [col + [[None] * len(col[0])] * (max_rows - len(col)) for col in columns]  

    # Transpose columns to rows for correct format
    # data_2d_list = list(map(list, zip(*col)))  # Transpose

    return columns#data_2d_list

# Example usage
folder = "./empirical_data/target_position_data_SW12_4x7/baseline_data"
# prefix = "rssi N1"  # Adjust to match your file naming pattern

sf = [entry.name for entry in os.scandir(folder) if entry.is_dir()]

# result_2d_list = read_and_concatenate_csv_files(folder, prefix)

# Print the final concatenated 2D list
print("\n🔹 Final 2D List:")
# for row in result_2d_list:
#     print(row)
    
for row in sf:
    print(row)
