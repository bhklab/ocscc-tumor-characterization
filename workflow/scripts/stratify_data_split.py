from damply import dirs
from pathlib import Path
from sklearn.model_selection import train_test_split
import csv
import pandas as pd
import shutil

dataset = "RADCURE_OCSCC"
pat_list_file = dirs.PROCDATA / dataset / "metadata" / "patient_list.csv"

gt_file = dirs.PROCDATA / dataset / "images" / f"mit_{dataset}" / f"mit_{dataset}_index-simple.csv"
gt_index_df = pd.read_csv(gt_file, index_col=0)

with (pat_list_file.open("r")) as f:
    reader = csv.reader(f)
    pat_list = [row[0] for row in reader]


gt, pred = train_test_split(pat_list, 
                            test_size=0.5, 
                            random_state=10, 
                            shuffle=True)

# Save out the patient lists for each split
gt_list_file = dirs.PROCDATA / dataset / "metadata" / "gt_patient_list.csv"
with (gt_list_file.open("w", newline='')) as f:
    writer = csv.writer(f)
    for pat in sorted(gt):
        writer.writerow([pat])

pred_list_file = dirs.PROCDATA / dataset / "metadata" / "pred_patient_list.csv"
with (pred_list_file.open("w", newline='')) as f:
    writer = csv.writer(f)
    for pat in sorted(pred):
        writer.writerow([pat])


# Create directories in results to copy image to based on split
results_dir = dirs.RESULTS / dataset / "images"
for id in pat_list:
    (results_dir / id).mkdir(parents=True, exist_ok=True)


# Copy over images and masks to results directory based on split
for id in gt:
    target_dir = results_dir / id
    # Copy over the CT nifti and the mask from the mit directory
    start_dir = dirs.PROCDATA / dataset / "images" / f"mit_{dataset}"
    ct_path = gt_index_df.loc[id, "filepath"].values[0]
    mask_path = gt_index_df.loc[id, "filepath"].values[1]
    
    shutil.copy(start_dir / ct_path, target_dir / Path(ct_path).name)
    shutil.copy(start_dir / mask_path, target_dir / "GTVp_mask.nii.gz")

for id in pred:
    target_dir = results_dir / id
    # Copy over the CT nifti from the mit directory
    start_dir = dirs.PROCDATA / dataset / "images" / f"mit_{dataset}"
    ct_path = gt_index_df.loc[id, "filepath"].values[0]
    shutil.copy(start_dir / ct_path, target_dir / Path(ct_path).name)

    # Copy over the mask niftis from the MedSAM2 predictions directory
    pred_mask_dir = dirs.PROCDATA / dataset / "images" / f"medsam_{dataset}" / "aligned_masks"
    shutil.copy(pred_mask_dir / f"{id}.nii.gz", target_dir / "GTVp_mask.nii.gz")