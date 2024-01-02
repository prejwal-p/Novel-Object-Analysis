"""
This file helps in analysing the videos and trajectories for novel object task. This tracks the mouse using DeepLabCut.

*********************************************************************************************************************
Here's how you use the functions available:
*********************************************************************************************************************
STEP 1 - Activate the DEEPLABCUT env
type "conda activate DEEPLABCUT" into the terminal

STEP 2 - Navigate to this folder
in the case of this session - "cd /home/prejwal/Downloads/FiberAnalysisTools/NovelObjectAnalysis/"

STEP 3.1 - To just track the mouse using DeepLabCut
"python analyze_novelobject.py {path_folder_which_contains_the_videos}"

STEP 3.2 - To track the mouse and analyze when the mouse explores the objects
"python analyze_novelobject.py {path_folder_which_contains_the_videos} -analyze"

STEP 3.3 - To create a labeled video of the mouse being tracked
"python analyze_novelobject.py {path_folder_which_contains_the_videos} -labeled_video"

STEP 3.2 - To just crop the video (Please note that you dont have to specify the crop_video in the above steps, the video cropper will be called automatically)
"python analyze_novelobject.py {path_folder_which_contains_the_videos} -crop_video"
"""


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import cv2
import numpy as np
import os
import sys
import deeplabcut
from config import Config
from helper import Helper
import glob
from parameters_gui import Get_Parameters



def format_data_from_deepof(path_to_h5, save_path):
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
        cols = data.columns.levels[1].values
        changed = False

        for key, val in bodyparts.items():
            if val in cols:
                data.columns.levels[1].values[data.columns.levels[1] == val] = key
                changed = True

        if changed == True:                
            data.to_hdf(os.path.join(save_path, file), key="df")


path = sys.argv[1]
config = Config()
get_parameters = Get_Parameters()
h = Helper()
shape_array = {}

if not os.path.exists(path):
    sys.exit("Please enter a valid path")

if len(path.split('/')[-1]) == 0:
    filenames = os.listdir(path)
elif [".avi", ".mp4"] in path.split('/')[-1]:
    filename = path.split('/')[-1]
    if filename in path:
        path = path.replace(filename, '')
    filenames = [filename] 
else:
    filenames = os.listdir(path)
     

video_files = []
for file in filenames:
    if "_temp" in file:
        file_format = "." + file.split(".")[1]
        file = file.split('_temp')[0] + file_format        

    if file.endswith(".mp4"):
        video_files.append(file)
    
    if file.endswith(".avi"):
        video_files.append(file)        


# Cropping The Video
for file in video_files:
    file_format = "." + file.split(".")[1]
    if "_temp" in file:
        file = file.split('_temp')[0] + file_format

    if not os.path.exists(os.path.join(path, file.split(".")[0])):
        os.mkdir(os.path.join(path, file.split(".")[0]))
        base_path = os.path.join(path, file.split(".")[0])
    else:
        base_path = os.path.join(path, file.split(".")[0])

    parameters = get_parameters.get_json(save_path=base_path)

    if parameters["track_mouse"] == 0:
        continue


    if not os.path.exists(os.path.join(path, file.split(".")[0], "video")):
        os.mkdir(os.path.join(path, file.split(".")[0], "video"))
        video_path = os.path.join(path, file.split(".")[0], "video")
    else:
        video_path = os.path.join(path, file.split(".")[0], "video")        

 

     
    if parameters["video_trimmed"] == 1:
        print("\n\n*******************************Trimming The Video*******************************\n")
        if not os.path.exists(os.path.join(path, "full_videos")):
            os.mkdir(os.path.join(path, "full_videos"))
        
        os.rename(os.path.join(path, file), os.path.join(path, "full_videos", file))
        
        h.VideoTrimmer(filename=file, save_path=path, video_path=os.path.join(path, "full_videos"))
    print("*******************************Done*******************************\n\n")


    print("\n\n*******************************Grabbing The Arena*******************************\n")
    print(file)
    if not os.path.exists(os.path.join(video_path, file.split(".")[0] + "_cropped.mp4")):
        s = h.CropArena(video_path=path, filename=file, dest_path=video_path)
        shape_array[file] = s
    else:
        crop_filename = file.split(".")[0] + "_cropped.mp4"    

    print("******************Detetecting Objects******************\n\n")

    if os.path.exists(os.path.join(video_path, file.split('.')[0] + "_arena.png")):
        # Getting The Balls Coordinates
        img = cv2.imread(os.path.join(video_path, file.split('.')[0] + "_arena.png"))

    if parameters["objects_found"] == 0:    
        object_coords, object_type, parameters = h.CropObjects(img, video_path, file, parameters, base_path)        
    print("*******************************Done*******************************\n\n")


if len(path.split('/')[-1]) == 0:
    filenames = os.listdir(path)
elif [".avi", ".mp4"] in path.split('/')[-1]:
    filename = path.split('/')[-1]
    if filename in path:
        path = path.replace(filename, '')
    filenames = [filename] 
else:
    filenames = os.listdir(path)
     

video_files = []
for file in filenames:
    if file.endswith(".mp4"):
        video_files.append(file)
    
    if file.endswith(".avi"):
        video_files.append(file)  



for file in video_files:


    if not os.path.exists(os.path.join(path, file.split(".")[0])):
        os.mkdir(os.path.join(path, file.split(".")[0]))
        base_path = os.path.join(path, file.split(".")[0])
    else:
        base_path = os.path.join(path, file.split(".")[0])

    if not os.path.exists(os.path.join(path, file.split(".")[0], "video")):
        os.mkdir(os.path.join(path, file.split(".")[0], "video"))
        video_path = os.path.join(path, file.split(".")[0], "video")
    else:
        video_path = os.path.join(path, file.split(".")[0], "video")  

    parameters = get_parameters.get_json(save_path=base_path)
    
    if parameters["track_mouse"] == 0 or parameters["objects_found"] == 0:
        continue

    print(f"\n\n*******************************Cropping Video - {file}*******************************\n")
    if not os.path.exists(os.path.join(video_path, file.split(".")[0] + "_cropped.mp4")):
        crop_filename = h.CropVideo(video_path=path, filename=file, dest_path=video_path, shape_array=shape_array[file])
    else:
        crop_filename = file.split(".")[0] + "_cropped.mp4"
    print("*******************************Done*******************************\n\n")

    if "-crop_video" not in sys.argv:  
        print("******************Analysing The Video Using DeepLabCut******************\n\n")
        if not os.path.exists(os.path.join(video_path, file.split('.')[0] + "_cropped" + config.extension + ".csv")):
            deeplabcut.analyze_videos(config.config_path, os.path.join(video_path, crop_filename), shuffle=1, trainingsetindex=0, gputouse=0, save_as_csv=True, allow_growth=True, destfolder=None, dynamic=(True, .5, 10))          
        print("\n\n*******************************Done*******************************\n\n")

    if parameters["labeled_video"] == 1:
        print("\n\n*******************************Creating Labelled Video*******************************\n") 
        
        format_data_from_deepof(path_to_h5=video_path, save_path=video_path)
        
        if not os.path.exists(os.path.join(path, file.split(".")[0], "video", "labeled_video")):
            os.mkdir(os.path.join(path, file.split(".")[0], "video", "labeled_video"))

            deeplabcut.create_labeled_video(config.config_path, os.path.join(video_path, crop_filename), videotype='mp4', filtered=False, save_frames=False)
            
            labeled_filename = [file for file in os.listdir(video_path) if file.endswith("_labeled.mp4")][0]
            os.rename(os.path.join(video_path, labeled_filename), os.path.join(video_path, "labeled_video", labeled_filename))
        print("\n\n*******************************Done*******************************\n\n")


