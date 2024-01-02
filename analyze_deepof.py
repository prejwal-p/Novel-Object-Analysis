from functions import AnalysisFunctions
import sys
import os
import glob
import pandas as pd
import cv2
from parameters_gui import Get_Parameters

f = AnalysisFunctions()

path = sys.argv[1]
get_parameters = Get_Parameters()

def get_delay(avi_path, csv_path, file):
    videofile = cv2.VideoCapture(os.path.join(avi_path, file + ".avi"))
    total_frames = int(videofile.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = videofile.get(cv2.CAP_PROP_FPS)
    csv_len = len(pd.read_csv(os.path.join(csv_path, file + "_signal.csv")))
    print(f"{file} : delay={(csv_len - total_frames) / 20}")

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

    parameters = get_parameters.get_json(save_path=base_path)

    if parameters["track_mouse"] == 0 or parameters["analyze_files"] == "0" or parameters["objects_found"] == 0:
        continue


    if not os.path.exists(os.path.join(base_path, "guppy")):
        os.mkdir(os.path.join(base_path, "guppy"))
        guppy_path = os.path.join(base_path, "guppy")
    else:
        guppy_path = os.path.join(base_path, "guppy")
    
    if not os.path.exists(os.path.join(path, file.split(".")[0], "video")):
        os.mkdir(os.path.join(path, file.split(".")[0], "video"))
        video_path = os.path.join(path, file.split(".")[0], "video")
    else:
        video_path = os.path.join(path, file.split(".")[0], "video")

    print("\n\n*******************************Analysing Trajectories*******************************\n")

    if not os.path.exists(os.path.join(base_path, "analysed")):
        os.mkdir(os.path.join(base_path, "analysed"))

    if not os.path.exists(os.path.join(base_path, "analysed", "deepof")):
        os.mkdir(os.path.join(base_path, "analysed", "deepof"))

    if not os.path.exists(os.path.join(base_path, "analysed", "tables")):
        os.mkdir(os.path.join(base_path, "analysed", "tables"))

    if not os.path.exists(os.path.join(base_path, "analysed", "results")):
        os.mkdir(os.path.join(base_path, "analysed", "results"))

    

    video_trim_offset = int(parameters["trim_offset"]) 

    time_offset = int(parameters["time_offset"]) 
    
    arena_distance = int(parameters["arena_distance"])

    # Parameters    
    offset =  + int(time_offset) + int(video_trim_offset)
    distance_threshold = int(parameters["distance_threshold"])

    videofile = cv2.VideoCapture(os.path.join(path, file))
    total_frames = int(videofile.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = videofile.get(cv2.CAP_PROP_FPS)  

    f.analyze_behavior(file=file, base_path=base_path, path=path, guppy_path=guppy_path, parameters=parameters, thresh=distance_threshold, offset=offset, arena_distance=arena_distance, total_frames=total_frames, frame_rate=frame_rate)

    print("Completed Analysing: ",file,"\n")