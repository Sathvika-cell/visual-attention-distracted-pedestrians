#cleaning
import os
import pandas as pd


root_dir = r"C:\Users\91961\Desktop\traffic_analysis"


target_cols = ['fix nr', 'fix dur (ms)', 'label']

for subdir, _, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".xls"):
            file_path = os.path.join(subdir, file)
            try:
            
                df = pd.read_csv(file_path, delimiter='\t')

                if all(col in df.columns for col in target_cols):
                    df_cleaned = df[target_cols]
                    df_cleaned.to_csv(file_path, index=False, sep='\t')  # overwrite with cleaned data
                    print(f"Cleaned: {file_path}")
                else:
                    print(f"Skipped (missing target cols): {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
#label shifting
import os
import pandas as pd


aoi_shift_map = {
    '2w': 0,
    '4w': 9,
    'hv': 18,
    'ir': 27,
    're': 36,
    'rem': 36,
    'remaining': 36
}

def detect_aoi_from_path(path):
    path_lower = path.replace("\\", "/").lower()
    for aoi in aoi_shift_map:
        if f"/{aoi}/" in path_lower:
            return aoi
    return None

def try_reading_delimited(file_path):
    for sep in [',', '\t', ';']:
        try:
            df = pd.read_csv(file_path, sep=sep, engine='python', encoding='utf-8')
            if df.shape[1] >= 3:
                return df.iloc[:, :3]
        except Exception:
            continue
    return None

def process_all_people_shift(root_dir):
    for person_folder in os.listdir(root_dir):
        person_path = os.path.join(root_dir, person_folder)
        if os.path.isdir(person_path):
            print(f"Shifting labels for {person_folder}...")
            process_shift_in_folder(person_path)

def process_shift_in_folder(folder_path):
    for dirpath, _, filenames in os.walk(folder_path):
        for file in filenames:
            if file.endswith(".xls"):
                full_path = os.path.join(dirpath, file)
                aoi = detect_aoi_from_path(full_path)

                if aoi is None:
                    print(f"AOI not detected: {full_path}")
                    continue

                df = try_reading_delimited(full_path)
                if df is None:
                    print(f"Could not read file: {full_path}")
                    continue

                try:
                    df.columns = ['fix_nr', 'fix_dur (ms)', 'label']
                    shift = aoi_shift_map[aoi]
                    df['label'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)
                    df['label'] = df['label'].apply(lambda x: x if x == 0 else x + shift)

                    df.to_csv(full_path, index=False)
                    print(f"Shifted +{shift}, saved: {full_path}")
                except Exception as e:
                    print(f"Error processing {full_path}: {e}")
source_folder = r"C:\Users\91961\Desktop\traffic_analysis"
process_all_people_shift(source_folder)

# Category Mapping 

category_map = {
    'vehicle': list(range(1, 28)),
    'signals': [28, 29],
    'sign boards': [31, 32],
    'tech': [33, 34],
    'advertisements': [35],
    'buildings': [39],
    'fellow pedestrians': [40, 41],
    'road elements': [30, 36, 37, 38, 42],
    'zoned out': [43]
}

remapped_labels = {
    'vehicle': 1,
    'signals': 2,
    'sign boards': 3,
    'tech': 4,
    'advertisements': 5,
    'buildings': 6,
    'fellow pedestrians': 7,
    'road elements': 8,
    'zoned out': 9
}

def get_category(label):
    for category, values in category_map.items():
        if label in values:
            return category
    return None

def process_all_people_remap(root_dir):
    for person_folder in os.listdir(root_dir):
        person_path = os.path.join(root_dir, person_folder)
        if os.path.isdir(person_path):
            print(f"Remapping labels for {person_folder}...")
            process_remap_in_folder(person_path)

def process_remap_in_folder(folder_path):
    for dirpath, _, filenames in os.walk(folder_path):
        for file in filenames:
            if file.endswith(".xls"):
                full_path = os.path.join(dirpath, file)

                try:
                    df = try_reading_delimited(full_path)
                    if df is None:
                        print(f"Could not read file: {full_path}")
                        continue

                    df.columns = ['fix_nr', 'fix_dur (ms)', 'label']
                    df['label'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)
                    df = df[df['label'] != 0]

                    df['type'] = df['label'].apply(get_category)
                    df = df[df['type'].notna()]

                    df['label'] = df['type'].map(remapped_labels)

                    df.to_csv(full_path, index=False)
                    print(f"Remapped and saved: {full_path}")
                except Exception as e:
                    print(f"Error processing {full_path}: {e}")

source_folder = r"C:\Users\91961\Desktop\vehicle_analysis"
process_all_people_shift(source_folder)
process_all_people_remap(source_folder)


#merging
import os
import shutil
import pandas as pd

def try_reading_excel_or_csv(file_path):
    try:
        df = pd.read_excel(file_path)
        print(f"Read as Excel: {file_path}")
        return df
    except Exception as e_excel:
        try:
            df = pd.read_csv(file_path, sep=None, engine='python')
            print(f"Read as CSV: {file_path}")
            return df
        except Exception as e_csv:
            print(f" Failed to read file: {file_path}\nExcel error: {e_excel}\nCSV error: {e_csv}")
            return None

def merge_activity_aoi_files(root_dir):
    for person_folder in os.listdir(root_dir):
        person_path = os.path.join(root_dir, person_folder)
        if not os.path.isdir(person_path):
            continue

        print(f"\nProcessing person: {person_folder}")

        for condition in ['HWW', 'IC', 'NO_CM']:
            condition_path = os.path.join(person_path, condition)
            if not os.path.isdir(condition_path):
                print(f"Condition folder missing: {condition_path}, skipping.")
                continue

            for activity in ['BASELINE', 'BB', 'LM', 'TLK', 'TXT']:
                activity_path = os.path.join(condition_path, activity)
                if not os.path.isdir(activity_path):
                    print(f" Activity folder missing: {activity_path}, skipping.")
                    continue

                print(f" Merging activity: {activity} for {condition}")

                merged_df = pd.DataFrame()
                aoi_folders = ['2W', '4W', 'HV', 'IR', 'REMAINING']

                for aoi in aoi_folders:
                    aoi_path = os.path.join(activity_path, aoi)
                    if not os.path.isdir(aoi_path):
                        print(f" AOI folder missing: {aoi_path}, skipping.")
                        continue

                    files = [f for f in os.listdir(aoi_path) if f.endswith('.xls') or f.endswith('.xlsx')]
                    if not files:
                        print(f"  No Excel file found in: {aoi_path}, skipping.")
                        continue

                    file_path = os.path.join(aoi_path, files[0])
                    df = try_reading_excel_or_csv(file_path)

                    if df is None:
                        continue

                    df = df.dropna(how='all')

                    if not all(col in df.columns for col in ['fix_nr', 'fix_dur (ms)', 'label', 'type']):
                        print(f" Required columns missing in {file_path}, skipping this AOI file.")
                        continue

                    merged_df = pd.concat([merged_df, df], ignore_index=True)

                # Save merged dataframe even if it's empty
                save_path = os.path.join(condition_path, f"{activity}.xlsx")
                merged_df.to_excel(save_path, index=False)

                if merged_df.empty:
                    print(f"Merged file saved (EMPTY): {save_path}")
                else:
                    print(f" Merged file saved: {save_path}")

                # Remove the AOI folders under activity
                try:
                    shutil.rmtree(activity_path)
                    print(f"Deleted folder: {activity_path}")
                except Exception as e:
                    print(f"ERROR deleting {activity_path}: {e}")
root_folder = r"C:\Users\91961\Desktop\activity_distractions1"

#vehicle analysis merging
import os
import shutil
import pandas as pd

def safe_read_excel_or_csv(file_path):
    try:
        if file_path.endswith('.xlsx'):
            return pd.read_excel(file_path, engine='openpyxl')
        elif file_path.endswith('.xls'):
            try:
                return pd.read_excel(file_path, engine='xlrd')
            except Exception:
                print(f" Trying to read {file_path} as CSV...")
                return pd.read_csv(file_path, encoding='utf-8', engine='python', on_bad_lines='skip')
        else:
            return None
    except Exception as e:
        print(f" Failed reading {file_path}: {e}")
        return None

def merge_and_preserve_aoi_files(root_dir):
    required_conditions = ['HWW', 'IC', 'NO_CM']
    required_aois = ['2W', '4W', 'HV']
    activities_to_merge = ['BB', 'LM', 'TLK', 'TXT']

    for person in os.listdir(root_dir):
        person_path = os.path.join(root_dir, person)
        if not os.path.isdir(person_path):
            continue

        for condition in required_conditions:
            condition_path = os.path.join(person_path, condition)
            if not os.path.isdir(condition_path):
                continue

            other_path = os.path.join(condition_path, 'OTHER')
            os.makedirs(other_path, exist_ok=True)

            for aoi in required_aois:
                merged_df = pd.DataFrame()

                for activity in activities_to_merge:
                    aoi_folder = os.path.join(condition_path, activity, aoi)
                    if not os.path.isdir(aoi_folder):
                        continue

                    files = [f for f in os.listdir(aoi_folder) if f.endswith(('.xls', '.xlsx'))]
                    if not files:
                        continue

                    file_path = os.path.join(aoi_folder, files[0])
                    df = safe_read_excel_or_csv(file_path)
                    if df is None or df.empty:
                        print(f"Skipping unreadable or empty file: {file_path}")
                        continue

                    df = df.dropna(how='all')

                    required_cols = ['fix_nr', 'fix_dur (ms)', 'label', 'type']
                    if not all(col in df.columns for col in required_cols):
                        print(f"Missing required columns in {file_path}, skipping.")
                        continue

                    merged_df = pd.concat([merged_df, df], ignore_index=True)

                save_path = os.path.join(other_path, f"{aoi}.xlsx")
                merged_df.to_excel(save_path, index=False)
                print(f"Saved merged AOI: {save_path}")

            for activity in activities_to_merge:
                act_path = os.path.join(condition_path, activity)
                if os.path.exists(act_path):
                    shutil.rmtree(act_path)
                    print(f"Deleted folder: {act_path}")

           
            for folder in ['BASELINE', 'OTHER']:
                folder_path = os.path.join(condition_path, folder)
                if not os.path.exists(folder_path):
                    continue

                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    name = item.replace('.xlsx', '') if item.endswith('.xlsx') else item
                    if name.upper() not in required_aois:
                        try:
                            if os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                            else:
                                os.remove(item_path)
                            print(f"Deleted extra AOI or folder: {item_path}")
                        except Exception as e:
                            print(f"Error deleting {item_path}: {e}")

root_dir = r"C:\Users\91961\Desktop\vehicle_analysis"
merge_and_preserve_aoi_files(root_dir)

#preprocessing
import os
import pandas as pd

def merge_activities_for_all_persons(root_dir):
    conditions = ['HWW', 'IC', 'NO_CM']
    activities = ['BASELINE', 'BB', 'LM', 'TLK', 'TXT']
    required_cols = ['fix_dur (ms)', 'label', 'type']

   
    for cond in conditions:
        cond_folder = os.path.join(root_dir, cond)
        os.makedirs(cond_folder, exist_ok=True)

    for person in os.listdir(root_dir):
        person_path = os.path.join(root_dir, person)
        if not os.path.isdir(person_path):
            continue
       
        if person in conditions:
            continue

        for cond in conditions:
            cond_path = os.path.join(person_path, cond)
            if not os.path.isdir(cond_path):
                print(f"Condition folder missing for {person}: {cond_path}, skipping.")
                continue

            dfs = []
            for act in activities:
                act_file = os.path.join(cond_path, f"{act}.xlsx")
                if not os.path.isfile(act_file):
                    print(f"Missing activity file for {person}/{cond}/{act}: {act_file}, skipping.")
                    
                    dfs.append(pd.DataFrame(columns=required_cols))
                    continue

                df = pd.read_excel(act_file)
                if not all(col in df.columns for col in required_cols):
                    print(f"Missing required columns in {act_file}, skipping.")
                    dfs.append(pd.DataFrame(columns=required_cols))
                    continue

                df_sub = df[required_cols].copy()
                df_sub.columns = [f"{col}_{act}" for col in required_cols]
                dfs.append(df_sub)

            merged_df = pd.concat(dfs, axis=1)

            out_dir = os.path.join(root_dir, cond)
            os.makedirs(out_dir, exist_ok=True)
            out_file = os.path.join(out_dir, f"{person}.csv")
            merged_df.to_csv(out_file, index=False)
            print(f"Saved merged CSV: {out_file}")

  
    for person in os.listdir(root_dir):
        person_path = os.path.join(root_dir, person)
        if os.path.isdir(person_path) and person not in conditions:
            import shutil
            shutil.rmtree(person_path)
            print(f"Deleted original folder: {person_path}")

root_directory = r"C:\Users\91961\Desktop\activity_distractions1" 
merge_activities_for_all_persons(root_directory)

#label shifting for vehicle analysis
import os
import pandas as pd


def map_label_to_category_type(label):
    try:
        label = int(label)
        if 1 <= label <= 9:
            return 1, '2W'
        elif 10 <= label <= 18:
            return 2, '4W'
        elif 19 <= label <= 27:
            return 3, 'HV'
    except:
        return None, None
    return None, None


def safe_read_file(filepath):
    try:
        return pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
    except Exception as e:
        print(f" Failed to read {filepath}: {e}")
        return None


def process_participant(participant_path, participant_name, output_root):
    print(f"\n Processing participant: {participant_name}")
    condition_folders = [f for f in os.listdir(participant_path) if os.path.isdir(os.path.join(participant_path, f))]

    for condition in condition_folders:
        condition_clean = condition.strip().upper()
        if condition_clean not in ['HWW', 'IC', 'NO_CM']:
            continue

        condition_path = os.path.join(participant_path, condition)
        merged_df = pd.DataFrame()

        for activity in os.listdir(condition_path):
            activity_path = os.path.join(condition_path, activity)
            if not os.path.isdir(activity_path):
                continue

            for aoi_name in ['2W', '4W', 'HV']:
                aoi_path = os.path.join(activity_path, aoi_name)
                if not os.path.isdir(aoi_path):
                    continue

                for file in os.listdir(aoi_path):
                    if not file.lower().endswith(('.csv', '.xls')):
                        continue
                    filepath = os.path.join(aoi_path, file)
                    df = safe_read_file(filepath)
                    if df is None or df.empty:
                        continue

                    df.columns = df.columns.str.strip().str.lower()
                    if not all(col in df.columns for col in ['fix nr', 'fix dur (ms)', 'label']):
                        continue

                    df = df[['fix nr', 'fix dur (ms)', 'label']].copy()
                    df = df.dropna(subset=['label'])
                    df['category'], df['type'] = zip(*df['label'].map(map_label_to_category_type))
                    df = df[df['type'].isin(['2W', '4W', 'HV'])]

                    if not df.empty:
                        merged_df = pd.concat([merged_df, df], ignore_index=True)

        if not merged_df.empty:
            output_dir = os.path.join(output_root, condition_clean)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{participant_name}.csv")
            merged_df.to_csv(output_path, index=False)
            print(f" Saved: {output_path}")
        else:
            print(f" No valid data for {participant_name} in {condition_clean}")


def process_all(root_dir):
    root_dir = os.path.abspath(root_dir)
    participants = [p for p in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, p))]
    for participant in participants:
        participant_path = os.path.join(root_dir, participant)
        process_participant(participant_path, participant, root_dir)
    print("\n All participants processed!")

if __name__ == '__main__':
   
    process_all(r"C:\Users\91961\Desktop\trail")

#FD calculations
import os
import zipfile
import pandas as pd
import warnings



ZIP_PATH = r"C:\Users\91961\Desktop\traffic_analysis.zip"
EXCEL_PATH = r"C:\Users\91961\Desktop\Participants List.xlsx"
EXTRACT_PATH = r"C:\Users\91961\Desktop\traffic_analysis"
OUTPUT_PATH = r"C:\Users\91961\Desktop\Participants List.xlsx"


if not os.path.exists(EXTRACT_PATH):
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_PATH)


DATA_ROOT = os.path.join(EXTRACT_PATH, "traffic_analysis")
ACTIVITIES = ["Baseline", "BB", "LM", "TLK", "TXT"]
AOI_FOLDERS = ["2W", "4W", "HV", "IR", "REM"]


df = pd.read_excel(EXCEL_PATH)
df.columns = [col.strip().capitalize() for col in df.columns]


for activity in ACTIVITIES:
    if activity not in df.columns:
        df[activity] = None


for participant in os.listdir(DATA_ROOT):
    part_path = os.path.join(DATA_ROOT, participant)
    if not os.path.isdir(part_path) or not participant.lower().startswith("p"):
        continue

    try:
        p_index = int(participant[1:])
    except ValueError:
        continue

    no_cm_path = os.path.join(part_path, "No_CM")
    if not os.path.exists(no_cm_path):
        continue

    for activity in ACTIVITIES:
        act_path = os.path.join(no_cm_path, activity)
        if not os.path.exists(act_path):
            continue

        total_durations = []

        for aoi in AOI_FOLDERS:
            aoi_path = os.path.join(act_path, aoi)
            if not os.path.exists(aoi_path):
                continue

            for file in os.listdir(aoi_path):
                if file.lower().endswith(".xls"):
                    try:
                        df_temp = pd.read_csv(os.path.join(aoi_path, file), encoding_errors='ignore')
                        if df_temp.shape[1] >= 2:
                            second_col = df_temp.columns[1]
                            duration_sum = pd.to_numeric(df_temp[second_col], errors='coerce').sum()
                            total_durations.append(duration_sum)
                            break
                    except:
                        continue

        if len(total_durations) >= 1:
            avg_dur = sum(total_durations) /len(total_durations) 
            df.loc[df["Participant"].str.strip().str.upper() == participant.upper(), activity] = avg_dur

df.to_excel(OUTPUT_PATH, index=False)
print(f"Updated Excel file saved to: {OUTPUT_PATH}")

import os
import pandas as pd


folder_path =   r"C:\Users\91961\Desktop\activity_distractions1\NO_CM"  
output_file = r"C:\Users\91961\Desktop\merged_noCM.csv" 


expected_columns = ['fix_dur (ms)_BASELINE',	'label_BASELINE',	'type_BASELINE',	'fix_dur (ms)_BB',	'label_BB',	'type_BB',	'fix_dur (ms)_LM',	'label_LM',	'type_LM',	'fix_dur (ms)_TLK',	'label_TLK',	'type_TLK',	'fix_dur (ms)_TXT',	'label_TXT',	'type_TXT'
]


merged_data = []


for filename in os.listdir(folder_path):
    if filename.endswith('.csv') or filename.endswith('.xls'): 
        file_path = os.path.join(folder_path, filename)
        try:
            df = pd.read_csv(file_path)

          
            df = df[[col for col in expected_columns if col in df.columns]]

            
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = pd.NA

            df = df[expected_columns]

            merged_data.append(df)

        except Exception as e:
            print(f"Could not process {filename}: {e}")


final_df = pd.concat(merged_data, ignore_index=True)


final_df.to_csv(output_file, index=False)
print(f"Merged file saved to {output_file}")































