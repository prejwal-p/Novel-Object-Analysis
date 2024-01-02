import cv2
import numpy as np
import os
import sys
from cropperGui import CropperGui
import pandas as pd
from tqdm import tqdm
import random
from datetime import datetime
import subprocess
#from segment_model import Segmenter
from parameters_gui import Get_Parameters
import tkinter as tk
from PIL import ImageTk, Image

class Helper:
    def __init__(self) -> None:
        pass

    def mil_convert(self, milliseconds):
        seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        return minutes, seconds


    def CropArena(self, video_path, filename, dest_path):
        videofile = cv2.VideoCapture(os.path.join(video_path, filename))
        total_frames = videofile.get(cv2.CAP_PROP_FRAME_COUNT)
        randomFrameNumber=random.randint(0, total_frames)
        # set frame position
        videofile.set(cv2.CAP_PROP_POS_FRAMES,randomFrameNumber)
        success, image = videofile.read()
        if success:
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
            c = CropperGui(image=img_gray, type="arena")        
        else:
            sys.exit("Unable To Process The Video")


        if c.arena_obtained:
            x = c.x
            y = c.y
            w = c.w
            h = c.h
        else:
            x = 0
            y = 0
            w = image.shape[1]
            h = image.shape[0]       

        cv2.imwrite(dest_path + "/" + filename.split('.')[0] + "_arena.png", image[y:y+h, x:x+w])
        return [x,y,w,h]

    def CropVideo(self, video_path, filename, dest_path, shape_array):
        image = cv2.imread(os.path.join(dest_path, filename.split('.')[0] + "_arena.png"))
        size = image.shape[:2]
        
        videofile = cv2.VideoCapture(os.path.join(video_path, filename))
        total_frames = videofile.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = videofile.get(cv2.CAP_PROP_FPS)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        video = cv2.VideoWriter(os.path.join(dest_path, filename.split(".")[0] + "_cropped.mp4"), fourcc, fps, (size[1],size[0]))
        crop_filename = os.path.join(dest_path, filename.split(".")[0] + "_cropped.mp4")
        
        

        print("Please wait, the video is being cropped........")
        for idx in tqdm(range(int(total_frames))):
            done, frame = videofile.read()
            
            if done:
                video.write(frame[shape_array[1]:shape_array[1]+shape_array[3], shape_array[0]:shape_array[0]+shape_array[2]])
            else:
                break
        video.release()
        return crop_filename

    def CropObjects(self, img, video_path, filename, parameters, config_path, thresh_1=150, thresh_2=200): 
        print("Please select the objects (region of interest).........") 
        # Convert to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                
        img_copy = img_gray.copy()

        c = CropperGui(image=img_gray, type="objects")
        detected_object = []
        if c.objects_obtained == 1:
            if len(c.detected_circles) > 0:
                detected_circles = c.detected_circles

                ids = 1 
                oa = []
                for i in detected_circles:
                    o = {}
                    center = (i[0], i[1])
                    cv2.circle(img_copy, center, 1, (0, 100, 100), 3)
                    radius = i[2]
                    cv2.circle(img_copy, center, radius, (255, 0, 255), 3)
                    o["id"] = ids
                    o["shape"] = "circle"
                    o["x"] = int(center[0])
                    o["y"] = int(center[1])
                    o["radius"] = int(radius)

                    ids = ids+1
                    oa.append(o)

                parameters["detected_objects"] = oa
                parameters["objects_found"] = 1
                Get_Parameters().save_json(parameters=parameters, save_path=config_path)

                cv2.imwrite(os.path.join(video_path, filename.split('.')[0] + "_detected_objects.png"), img_copy)
                detected_object = detected_circles
            if len(c.detected_rect) > 0:
                detected_rect = c.detected_rect
                
                ids = 1
                oa = []
                for i in detected_rect:
                    o = {}
                    
                    img_copy = cv2.rectangle(img_copy, (i[0], i[1]), (i[2], i[3]), (255,0,0), 2)
                    o["id"] = ids
                    o["shape"] = "rectangle"
                    o["x_start"] = int(i[0])
                    o["x_end"] = int(i[2])
                    o["y_start"] = int(i[1])
                    o["y_end"] = int(i[3])
                    ids = ids+1
                    oa.append(o)

                parameters["detected_objects"] = oa
                parameters["objects_found"] = 1               
                Get_Parameters().save_json(parameters=parameters, save_path=config_path)

                cv2.imwrite(os.path.join(video_path, filename.split('.')[0] + "_detected_objects.png"), img_copy)  
                detected_object = detected_rect
        else:
            parameters["detected_objects"] = []
            parameters["objects_found"] = 0            
        return detected_object, c.object_shape.get(), parameters

    def VideoTrimmer(self, video_path, filename, save_path):
        inp = os.path.join(video_path, filename)
        out = os.path.join(save_path, filename)

        parameters = Get_Parameters().get_json(save_path=os.path.join(save_path, filename.split(".")[0]))

        if parameters["video_trimmed"] == 1:
            start=f"{parameters['trim_start_hours']}:{parameters['trim_start_min']}:{parameters['trim_start_seconds']}" #specify start time in hh:mm:ss
            end=f"{parameters['trim_end_hours']}:{parameters['trim_end_min']}:{parameters['trim_end_seconds']}"   #specify end time in hh:mm:ss        

            print("Trimming the video\n")
            process = subprocess.Popen(['ffmpeg', '-i', inp, "-ss", start, "-to", end, "-c:v", "copy", "-c:a", "copy", out],
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            stdout, stderr


    def resample_video(self, video_path, filename):
        print(f"\n\n*******************************Resampling Video - {filename}*******************************\n") 
        cap = cv2.VideoCapture(os.path.join(video_path, filename))
        success, frame = cap.read()
        image_shape = (frame.shape[1], frame.shape[0])
        cap.release()

        cap = cv2.VideoCapture(os.path.join(video_path, filename))
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        record_path = os.path.join(video_path, filename.split('_temp')[0] + '.mp4')

        d = pd.read_csv(os.path.join(video_path, filename.split('_temp')[0] + '.csv'))
        
        average_frame_rate = 1/np.mean(np.diff(np.array(d['record_time'].values - d['record_time'][0])))

        videoWriter = cv2.VideoWriter(record_path, fourcc, average_frame_rate, image_shape)
        for i in tqdm(range(int(total_frames))):
            success, frame = cap.read()
            if success:
                videoWriter.write(frame)
        videoWriter.release()   
        cap.release()
        return str(filename.split('_temp')[0] + '.mp4')
