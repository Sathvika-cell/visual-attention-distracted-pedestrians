import os
import shutil

# Define the root folder path
root_path = r"C:\Users\91961\Desktop\luck"

# Subfolders that need to be restructured
category_folders = ['HWW', 'IC', 'NO_CM']
sub_levels = ['BASELINE', 'BB', 'LM', 'TLK', 'TXT']
vehicle_types = ['2W', '4W', 'HV', 'IR', 'REMAINING']

def safe_rearrange():
    print("Starting rearrange process...")

    # List the folders in the root directory
    for p_folder in os.listdir(root_path):
        p_folder_path = os.path.join(root_path, p_folder)

        # Only process folders starting with 'P_' (e.g., P_some_index)
        if not os.path.isdir(p_folder_path) or not p_folder.startswith('P_'):
            continue

        print(f"Found folder: {p_folder_path}")  # Debug log for found folders

        # Create the new structure (HWW, IC, NO_CM) under each P_ folder
        for cat in category_folders:
            new_cat_dir = os.path.join(p_folder_path, cat)
            if not os.path.exists(new_cat_dir):
                os.makedirs(new_cat_dir, exist_ok=True)
                print(f"Created category directory: {new_cat_dir}")  # Debug log for directory creation

            # Create sublevel directories (BASELINE, BB, LM, TLK, TXT)
            for sub in sub_levels:
                new_sub_dir = os.path.join(new_cat_dir, sub)
                if not os.path.exists(new_sub_dir):
                    os.makedirs(new_sub_dir, exist_ok=True)
                    print(f"Created sublevel directory: {new_sub_dir}")  # Debug log for sublevel directory creation

            # Create vehicle folders (2W, 4W, HV, IR, REMAINING) inside each category
            for vehicle in vehicle_types:
                new_vehicle_dir = os.path.join(new_cat_dir, vehicle)
                if not os.path.exists(new_vehicle_dir):
                    os.makedirs(new_vehicle_dir, exist_ok=True)
                    print(f"Created vehicle directory: {new_vehicle_dir}")  # Debug log for vehicle directory creation

        # Now we need to move and rename the files
        for vehicle in vehicle_types:
            old_vehicle_path = os.path.join(p_folder_path, vehicle)

            if not os.path.isdir(old_vehicle_path):
                continue

            # Debug log for the vehicle folder
            print(f"Processing vehicle folder: {old_vehicle_path}")

            # Process each category (HWW, IC, NO_CM)
            for cat in category_folders:
                old_cat_path = os.path.join(old_vehicle_path, cat)

                if not os.path.isdir(old_cat_path):
                    continue

                # Debug log for the category folder
                print(f"Processing category folder: {old_cat_path}")

                # Process each sublevel (BASELINE, BB, LM, TLK, TXT)
                for sub in sub_levels:
                    old_sub_path = os.path.join(old_cat_path, sub)

                    if not os.path.isdir(old_sub_path):
                        continue

                    # Debug log for the sublevel folder
                    print(f"Processing sublevel folder: {old_sub_path}")

                    # Move files from the deepest subfolder to the new location
                    for file in os.listdir(old_sub_path):
                        file_ext = os.path.splitext(file)[1].lower()

                        if file_ext in ['.xlsx', '.xls', '.accdb']:
                            # Rename the file based on the folder name (e.g., 2W.xlsx)
                            new_name = f"{vehicle}{file_ext}"

                            # Define the target folder for the new structure
                            target_folder = os.path.join(p_folder_path, cat, sub, vehicle)
                            src_file = os.path.join(old_sub_path, file)
                            dst_file = os.path.join(target_folder, new_name)

                            # Move the file to the new location
                            if not os.path.exists(dst_file):  # Only move if the file doesn't already exist
                                print(f"Moving file: {src_file} -> {dst_file}")
                                shutil.move(src_file, dst_file)
                            else:
                                print(f"Skipping move: {dst_file} already exists.")

    print("Rearranging complete!")

# Run the rearrange function
safe_rearrange()