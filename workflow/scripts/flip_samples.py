from damply import dirs
from pathlib import Path
import csv
import pandas as pd
import shutil

def shift_RADCURE_id(sample_id:str,
                     shift:int =17):
    """Take RADCURE SampleID like RADCURE-0001_0001 and add a shift to both numbers."""
    id_strs = sample_id.split('-')[1].split('_')
    id_nums = [int(id) + 17 for id in id_strs]
    return f"RADCURE-{id_nums[0]:04d}_{id_nums[1]:04d}"



dataset = "RADCURE_OCSCC"

# Load in mit index to use to get filepaths
gt_file = dirs.PROCDATA / dataset / "images" / f"mit_{dataset}" / f"mit_{dataset}_index-simple.csv"
gt_index_df = pd.read_csv(gt_file, index_col=0)

# Read in the ground truth list
gt_list_file = dirs.PROCDATA / dataset / "metadata" / "gt_patient_list.csv"
with(gt_list_file.open("r")) as f:
    gt_file= csv.reader(f)
    gt_list = [line[0] for line in gt_file]

# Read in the predicted list
pred_list_file = dirs.PROCDATA / dataset / "metadata" / "pred_patient_list.csv"
with (pred_list_file.open("r")) as f:
    pred_file=csv.reader(f)
    pred_list = [line[0] for line in pred_file]

flip_pred_list = [shift_RADCURE_id(sample_id) for sample_id in gt_list]
flip_gt_list = [shift_RADCURE_id(sample_id) for sample_id in pred_list]

#Create directories in results to copy image to based on split
results_dir = dirs.RESULTS / dataset / "images_reproducibility"
shifted_pat_list = flip_pred_list + flip_gt_list
for id in shifted_pat_list:
    (results_dir / id).mkdir(parents=True, exist_ok=True)

# Copy the mit images over this time for those originally marked as "pred"
for idx, sample_id in enumerate(flip_gt_list):
    target_dir = results_dir / sample_id
    start_dir = dirs.PROCDATA / dataset / "images" / f"mit_{dataset}"
    orig_sample_id = pred_list[idx]
    ct_path = gt_index_df.loc[orig_sample_id, "filepath"].values[0]
    mask_path = gt_index_df.loc[orig_sample_id, "filepath"].values[1]

    shutil.copy(start_dir / ct_path, target_dir / Path(ct_path).name)
    shutil.copy(start_dir / mask_path, target_dir / "GTVp_mask.nii.gz")

for idx, sample_id in enumerate(flip_pred_list):
    target_dir = results_dir / sample_id
    # Copy over the CT nifti from the mit directory
    start_dir = dirs.PROCDATA / dataset / "images" / f"mit_{dataset}"
    orig_sample_id = gt_list[idx]
    ct_path = gt_index_df.loc[orig_sample_id, "filepath"].values[0]
    shutil.copy(start_dir / ct_path, target_dir / Path(ct_path).name)

    # Copy over the mask niftis from the MedSAM2 predictions directory
    pred_mask_dir = dirs.PROCDATA / dataset / "images" / f"medsam_{dataset}" / "aligned_masks"
    shutil.copy(pred_mask_dir / f"{orig_sample_id}.nii.gz", target_dir / "GTVp_mask.nii.gz")