from config import Config
from parameters_gui import Get_Parameters
import sys
import os
sys.path.append(os.path.abspath("/home/prabhaka/GuPPy-main/GuPPy/"))
from saveStoresList import execute, readtsq, import_np_doric_csv, saveStorenames
from pathlib import Path
import json
import pandas as pd
import subprocess
import numpy as np
import h5py
import shutil
import seaborn as sns
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 300

path = sys.argv[1]
config = Config()
get_parameters = Get_Parameters()

folders = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]


def get_plots(dff, event, plot_path, filename):
    event_indices = event['timestamps'].values * 20
    
    start_time = -5
    end_time = 10
    
    start_idx = start_time*20
    end_idx = end_time*20
    
    vals = []
    
    for e in event_indices:
        vals.append(dff['dff'].values[e+start_idx:e+end_idx])
    
    time = np.around(np.arange(start_time, end_time, 1/20), decimals=1)
    psth = pd.DataFrame(vals).T.fillna(0)
    psth.index = time
    psth.columns = event['timestamps'].values
    
    plt.figure()
    ax = sns.heatmap(psth.T)
    yticks = ax.get_yticks()
    diff = np.mean(np.diff(yticks))
    center = 5*20
    
    ax.vlines(center, ymin=yticks[0]-diff, ymax=yticks[-1]+diff, colors="green")
    plt.xticks(rotation=70)
    plt.yticks(rotation=0)
    plt.savefig(os.path.join(plot_path, filename + "_psth.png"))
    
    plt.figure()
    mean = pd.DataFrame({"time":np.tile(np.arange(start_time, end_time, 1/20), len(event_indices)), "vals":psth.values.T.ravel()})
    sns.lineplot(data=mean, x="time", y="vals")
    plt.savefig(os.path.join(plot_path, filename + "_psth_mean.png"))



for folder in folders:
    base_path = os.path.join(path, folder)
    control_file = os.path.join(base_path, "guppy", folder + "_C.csv")
    signal_file = os.path.join(base_path, "guppy", folder + "_S.csv")

    if os.path.exists(os.path.join(base_path, "guppy", folder + "_dff.csv")) and os.path.exists(os.path.join(base_path, "guppy", folder + "_transients.csv")):
        continue

    if os.path.exists(os.path.join(base_path, "guppy")) and os.path.exists(control_file) and os.path.exists(signal_file):
        print(f"\n\n*******************************Guppy Analysis - {folder}*******************************\n")

        guppy_path = os.path.join(base_path, "guppy")

        parameters = get_parameters.get_json(save_path=base_path)

        if parameters["lvm_color_channel"] != "none":
            if not os.path.exists(os.path.join(guppy_path, "guppy_output_1")):
                os.mkdir(os.path.join(guppy_path, "guppy_output_1"))
                guppy_output_path = os.path.join(guppy_path, "guppy_output_1")
            else:
                guppy_output_path = os.path.join(guppy_path, "guppy_output_1")

            # Creating The StoreNames File
            analyzed_files = [f for f in os.listdir(guppy_path) if f.endswith(".csv")]
            storelist = {}
            event_files = []

            for file in analyzed_files:
                if file.endswith("_S.csv"):
                    storelist[file.split(".")[0]] = "signal_" + file.split("_")[0]
                elif file.endswith("_C.csv") and parameters["use_isosbestic"]:
                    storelist[file.split(".")[0]] = "control_" + file.split("_")[0]
                elif file.endswith("_C.csv") and parameters["use_isosbestic"] == 0:
                    continue
                else:
                    storelist[file.split(".")[0]] = file.split("_")[-1].split(".")[0]
                    event_files.append(file)

            pd.DataFrame(storelist, index=[0]).to_csv(os.path.join(guppy_output_path, "storesList.csv"), index=False)

            inputParameters = {'abspath': base_path, 
                'folderNames': [guppy_path], 
                'numberOfCores': 2, 
                'combine_data': False, 
                'isosbestic_control': [True if parameters["use_isosbestic"] else False][0], 
                'timeForLightsTurnOn': 0, 
                'filter_window': parameters["filter_window"], 
                'removeArtifacts': True, 
                'artifactsRemovalMethod': 'concatenate', 
                'noChannels': 2, 
                'zscore_method': 'standard z-score', 
                'baselineWindowStart': 0, 
                'baselineWindowEnd': 0, 
                'nSecPrev': -5, 
                'nSecPost': 10, 
                'computeCorr': False, 
                'timeInterval': 2, 
                'bin_psth_trials': 0, 
                'use_time_or_trials': 'Time (min)', 
                'baselineCorrectionStart': -5, 
                'baselineCorrectionEnd': 0, 
                'peak_startPoint': [-5.0, 0.0, 5.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan], 
                'peak_endPoint': [0.0, 3.0, 10.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan], 
                'selectForComputePsth': 'z_score', 
                'selectForTransientsComputation': 'z_score', 
                'moving_window': parameters["moving_window"], 
                'highAmpFilt': 2, 
                'transientsThresh': 3, 
                'plot_zScore_dff': 'None', 
                'visualize_zscore_or_dff': 'None', 
                'folderNamesForAvg': [], 
                'averageForGroup': False, 
                'visualizeAverageResults': False,
                "curr_dir":"/home/prabhaka/GuPPy-main/"}
            try:
                subprocess.call(["python", os.path.join("/home/prabhaka/GuPPy-main/","GuPPy","readTevTsq.py"), json.dumps(inputParameters)])
                subprocess.call(["python", os.path.join("/home/prabhaka/GuPPy-main/","GuPPy","preprocess.py"), json.dumps(inputParameters)])
                subprocess.call(["python", os.path.join("/home/prabhaka/GuPPy-main/","GuPPy","computePsth.py"), json.dumps(inputParameters)])

                # Organising The Data
                dff_file = [f for f in os.listdir(guppy_output_path) if f.endswith(".hdf5") and "dff" in f][0]
                
                with h5py.File(os.path.join(guppy_output_path, dff_file), "r") as f:
                    guppy_dff = f["data"][()]
                
                pd.DataFrame({"dff": guppy_dff}).to_csv(os.path.join(guppy_path, folder + "_dff.csv"), index=False)

                peak_file = [f for f in os.listdir(guppy_output_path) if f.endswith(".csv") and "transientsOccurrences" in f][0]      
                shutil.copy(os.path.join(guppy_output_path, peak_file), os.path.join(guppy_path, folder + "_transients.csv"))

                        # Plotting The Data
                if not os.path.exists(os.path.join(guppy_path, "plots")):
                    os.mkdir(os.path.join(guppy_path, "plots"))
                    plot_path = os.path.join(guppy_path, "plots")
                else:
                    plot_path = os.path.join(guppy_path, "plots")

                dff = pd.read_csv(os.path.join(guppy_path, folder + "_dff.csv"))
                for event_name in event_files:
                    event = pd.read_csv(os.path.join(guppy_path, event_name))
                    get_plots(dff, event, plot_path, event_name.split(".")[0])
                
                #event = pd.read_csv(os.path.join(guppy_path, folder + "_transients.csv"))
                #get_plots(dff, event, plot_path, folder + "_transients")
                print(f"\n\n*********************************Succesfully Analysed - {folder}****************************\n")
            except Exception:
                print(f"\n\n/////////////////////////////////ERROR ANALYSING - {folder}/////////////////////////////////\n")
                continue




