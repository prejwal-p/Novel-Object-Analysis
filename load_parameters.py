import os
import sys
from config import Config
import tkinter as tk
import subprocess
from tkinter import filedialog
from tkinter import messagebox
from parameters_gui import Get_Parameters   
  
config = Config()
get_parameters = Get_Parameters()

root = tk.Tk()
root.withdraw()

path = filedialog.askdirectory()

root.destroy()



if not os.path.exists(path):
    sys.exit("Please enter a valid path")

filenames = os.listdir(path)     

video_files = []
for file in filenames:
    if file.endswith(".mp4"):
        video_files.append(file)
    
    if file.endswith(".avi"):
        video_files.append(file)  

load_files = []

for file in video_files:
    file_format = "." + file.split(".")[1]
    if "_temp" in file:
        file = file.split('_temp')[0] + file_format
    
    if not os.path.exists(os.path.join(path, file.split(".")[0], "config.json")):
        load_files.append(file)

if len(load_files) > 1:
    root = tk.Tk()
    root.withdraw()

    reply = messagebox.askquestion("Multiple videos detected", "Do you want to set these parameters for all the videos?")

    root.destroy()
else:
    reply = "no"


if reply == "yes":
    parameters = get_parameters.set_parameters(filename="All")
    
    for file in load_files:
        if "_temp" in file:
            file = file.split('_temp')[0] + file_format

        if not os.path.exists(os.path.join(path, file.split(".")[0])):
            os.mkdir(os.path.join(path, file.split(".")[0]))
            save_path = os.path.join(path, file.split(".")[0])
        else:
            save_path = os.path.join(path, file.split(".")[0])

        get_parameters.save_json(parameters=parameters, save_path=save_path)

else:        
    for file in load_files:
        parameters = get_parameters.set_parameters(filename=file)
        
        if "_temp" in file:
            file = file.split('_temp')[0] + file_format

        if not os.path.exists(os.path.join(path, file.split(".")[0])):
            os.mkdir(os.path.join(path, file.split(".")[0]))
            save_path = os.path.join(path, file.split(".")[0])
        else:
            save_path = os.path.join(path, file.split(".")[0])

        get_parameters.save_json(parameters=parameters, save_path=save_path)  


print(path+"/")