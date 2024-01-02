import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import os, warnings
warnings.filterwarnings('ignore')

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

import cv2
import numpy as np
import os
from helper import Helper
from config import Config
import pickle
import deepof.data
import deepof.visuals

class AnalysisFunctions:

    def __init__(self) -> None:
        self.h = Helper()
        self.c = Config()

    def analyze_behavior(self, file, path, base_path, guppy_path, parameters, frame_rate, total_frames, thresh=50, offset=0, arena_distance=500):
        filename = file.split(".")[0]
        analysed_path = os.path.join(base_path, "analysed")
        results_path = os.path.join(analysed_path, "results")

        if parameters["track_mouse"] == 0 or parameters["analyze_files"] == "0":
            return

        # Creating DeepOF Project and Analysed DeepOF
        self.format_data_for_deepof(os.path.join(base_path, "video"), os.path.join(analysed_path, "tables"))

        project_path = os.path.join(analysed_path, "deepof")
        video_path = os.path.join(base_path, "video")
        table_path = os.path.join(analysed_path, "tables")

        if not os.path.exists(os.path.join(analysed_path, "deepof", filename, "Coordinates", "deepof_coordinates.pkl")):
            my_deepof_project = deepof.data.Project(
                    project_path=project_path,
                    video_path=video_path,
                    table_path=table_path,
                    project_name=filename,
                    arena="circular-autodetect",
                    bodypart_graph="deepof_14",
                    video_format=".mp4",
                    video_scale=arena_distance,
                    enable_iterative_imputation=10,
                    smooth_alpha=1,
                    exp_conditions=None,
                    )
            my_deepof_project = my_deepof_project.create(force=True)
        else:
            my_deepof_project = deepof.data.load_project(os.path.join(project_path, filename))            

        behavior_data = my_deepof_project.supervised_annotation()

        #signal_data = pd.read_csv(os.path.join(guppy_path, filename + "_S.csv"))

        try:
            object_coords = parameters["detected_objects"]
        except:
            object_coords = []

        animal_id = list(my_deepof_project.get_coords().keys())[0]
        coords = my_deepof_project.get_coords()[animal_id]        
        behavior_data[animal_id].to_csv(os.path.join(results_path, filename + "_behavior_data.csv"), index=False)
        
        # Calculating object exploration
        coords = coords.reset_index()
        
        nose_coords = coords["Nose"]

        if os.path.exists(os.path.join(path, filename + ".csv")):
            at = pd.read_csv(os.path.join(path, filename + ".csv"))['accquisition_times'].values
            at = at - at[0]
            nose_coords["frame_time"] = at

            # Modifying Time
            total_time = at[-1]
            time_array = np.arange(0, total_time, 1/(len(nose_coords)/total_time))
            datetime_time_array = [divmod(i, 60) for i in time_array]
        else:
            t = np.arange(0, (len(nose_coords)/frame_rate), 1/frame_rate)
            if len(nose_coords) != len(t):
                min_length = min(len(nose_coords), len(t))
                nose_coords = nose_coords[:min_length]
                t = t[:min_length]

            nose_coords["frame_time"] = t
            datetime_time_array = [divmod(i, 60) for i in nose_coords["frame_time"]]
            time_array = nose_coords["frame_time"].values


        if object_coords != []:
            img = cv2.imread(os.path.join(base_path, "video", filename + "_detected_objects.png"))
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                
            img_copy = img_gray.copy()
            nose_near_obj = pd.DataFrame()

            for obj in object_coords:
                t = obj["shape"]
                if t == "circle":
                    circle_1 = ((nose_coords["x"].values - obj["x"])**2 + (nose_coords["y"].values - obj["y"])**2) <= (obj["radius"] + thresh)**2
                    nose_near_obj = pd.concat([nose_near_obj, nose_coords[circle_1]])             
                    center = (obj["x"], obj["y"])
                    radius = obj["radius"] + thresh                
                    cv2.circle(img_copy, center, radius, (255, 0, 255), 3)

                elif t == "rectangle":
                    center = [(obj["x_start"] + obj["x_end"]) / 2, (obj["y_start"] + obj["y_end"]) / 2] 
                    radius = np.sqrt((center[0] - obj["x_start"])**2 + (center[1] - obj["y_start"])**2)
                    circle = ((nose_coords["x"].values - center[0])**2 + (nose_coords["y"].values - center[1])**2) <= (radius + thresh)**2
                    nose_near_obj = pd.concat([nose_near_obj, nose_coords[circle]]) 

                    cv2.circle(img_copy, (int(center[0]), int(center[1])), int(radius + thresh), (255, 0, 255), 3) 

            cv2.imwrite(os.path.join(base_path, "video", filename + "_detected_objects.png"), img_copy)

            
            if len(coords) != len(datetime_time_array):
                min_length = min(len(coords), len(datetime_time_array))
                coords = coords[:min_length]
                datetime_time_array = datetime_time_array[:min_length]
            coords["index"] = datetime_time_array
            ta = [datetime_time_array[int(i)] for i in nose_near_obj.index.to_list()]
            nose_near_obj["time"] = ta

            done = False
            start_idx = 0
            curr_idx = 0
            correct_idx = []
            dur_array = []
            time = [time_array[int(i)] for i in nose_near_obj.index.to_list()]

            if len(time) != 0:
                while done==False:
                    if curr_idx == 0:
                        correct_idx.append(curr_idx)
                        curr_idx = curr_idx + 1
                    
                    elif curr_idx == len(time):
                        dur_array.append(time[curr_idx-1] - time[start_idx])
                        done = True
                        
                    elif time[curr_idx] - time[curr_idx - 1] > 2:
                        correct_idx.append(curr_idx)
                        dur_array.append(time[curr_idx-1] - time[start_idx])        
                        start_idx = curr_idx
                        curr_idx = curr_idx + 1
                    
                    else:
                        curr_idx = curr_idx + 1
            
            # Removing error values       
            timestamps = nose_near_obj.iloc[correct_idx]

            timestamps["duration"] = dur_array

            timestamps = timestamps[timestamps["duration"] > 0.100]

            indices = timestamps.index
            err_idx = []
            threshold = 250
            for idx in indices:
                if idx == 0 and ((nose_coords.iloc[idx]["x"] - nose_coords.iloc[idx+1]["x"]) > threshold or (nose_coords.iloc[idx]["y"] - nose_coords.iloc[idx+1]["y"]) > threshold):
                    err_idx.append(idx)
                elif (nose_coords.iloc[idx]["x"] - nose_coords.iloc[idx-1]["x"]) > threshold or (nose_coords.iloc[idx]["y"] - nose_coords.iloc[idx-1]["y"]) > threshold:
                    err_idx.append(idx)

            timestamps = timestamps.drop(index=err_idx)

            timestamps["timestamps"] = np.array([time_array[int(i)] for i in timestamps.index.to_list()]).astype(int) + offset
            timestamps.to_csv(os.path.join(results_path, filename + "_object_explore.csv"), index=False)
            
            if len(np.array([time_array[int(i)] for i in timestamps.index.to_list()]).astype(int)) > 0:
                pd.DataFrame({"timestamps": np.array([time_array[int(i)] for i in timestamps.index.to_list()]).astype(int) + offset}).to_csv(os.path.join(guppy_path, filename + "_obj_explore.csv"), index=False)

        
        coords.to_csv(os.path.join(results_path, filename + "_coordinates.csv"), index=False)

        behavior_data = behavior_data[animal_id].reset_index()
        behavior_data["time"] = datetime_time_array
        behavior_data = behavior_data.drop(columns="index")

        for act in behavior_data.columns[:4]:
            data = behavior_data[behavior_data[act] == 1]
            
            done = False
            start_idx = 0
            curr_idx = 0
            correct_idx = []
            dur_array = []
            time = [time_array[int(i)] for i in data.index.to_list()]
            if len(time) != 0:
                while done==False:
                    if curr_idx == 0:
                        correct_idx.append(curr_idx)
                        curr_idx = curr_idx + 1

                    elif curr_idx == len(time):
                        dur_array.append(time[curr_idx-1] - time[start_idx])
                        done = True

                    elif time[curr_idx] - time[curr_idx - 1] > 2:
                        correct_idx.append(curr_idx)
                        dur_array.append(time[curr_idx-1] - time[start_idx])        
                        start_idx = curr_idx
                        curr_idx = curr_idx + 1

                    else:
                        curr_idx = curr_idx + 1

                timestamps = data.iloc[correct_idx]
                timestamps["duration"] = dur_array
                timestamps = timestamps[timestamps["duration"] > 0.25]

                timestamps.to_csv(os.path.join(results_path, filename + "_" + act + ".csv"), index=False)
                
                if len(np.array([time_array[int(i)] for i in timestamps.index.to_list()]).astype(int)) > 0:
                    pd.DataFrame({"timestamps": np.array([time_array[int(i)] for i in timestamps.index.to_list()]).astype(int) + offset}).to_csv(os.path.join(guppy_path, filename + "_" + act + ".csv"), index=False)



    def format_data_for_deepof(self, path_to_h5, save_path):
        # path: Provide the path to .h5 files
        f = os.listdir(path_to_h5)
        filenames = [file for file in f if file.endswith(".h5")]

        bodyparts = {
            "nose":"Nose",
            "left_ear":"Left_ear",
            "right_ear":"Right_ear",
            "neck":"Spine_1",
            "mouse_center":"Center",
            "left_shoulder":"Left_fhip",
            "right_shoulder":"Right_fhip",
            "left_hip":"Left_bhip",
            "right_hip":"Right_bhip",
            "mid_backend2":"Spine_2",
            "tail_base":"Tail_base",
            "tail2":"Tail_1",
            "tail4":"Tail_2",
            "tail_end":"Tail_tip"
        }
        for file in filenames:
            data = pd.read_hdf(os.path.join(path_to_h5, file))
            
            for key, val in bodyparts.items():
                data.columns.levels[1].values[data.columns.levels[1] == key] = val

            data.to_hdf(os.path.join(save_path, file), key="df")