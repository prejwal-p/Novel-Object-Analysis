import os
import json
import tkinter as tk

class Get_Parameters:
    def __init__(self) -> None:
        pass

    def set_parameters(self, filename):
        parameters = {}

        # Create GUI
        root = tk.Tk()
        root.title("Parameter Input")
        root.attributes("-fullscreen", True)

        # Trimming The Video
        trim_label = tk.Label(
            root, text=f"Parameters For Trimming - {filename}")
        trim_label.pack()

        trim_ans_label = tk.Label(root, text="Do you want to trim the videos?")
        trim_ans_label.pack()

        # Create radio button
        trim_ans_var = tk.StringVar(value="no")
        trim_ans_yes = tk.Radiobutton(
            root, text="Yes", variable=trim_ans_var, value="yes")
        trim_ans_no = tk.Radiobutton(
            root, text="No", variable=trim_ans_var, value="no")
        trim_ans_yes.pack()
        trim_ans_no.pack()

        trim_start_label = tk.Label(
            root, text="Please specify the start time (Make sure to add a 0 if it is a single digit. Ex: '08'):")
        trim_start_label.pack()

        trim_start_hours_label = tk.Label(root, text="hours:")
        trim_start_hours_label.pack()
        trim_start_hours_entry = tk.Entry(root, state="disabled")
        trim_start_hours_entry.pack()

        trim_start_min_label = tk.Label(root, text="minutes:")
        trim_start_min_label.pack()
        trim_start_min_entry = tk.Entry(root, state="disabled")
        trim_start_min_entry.pack()

        trim_start_seconds_label = tk.Label(root, text="seconds:")
        trim_start_seconds_label.pack()
        trim_start_seconds_entry = tk.Entry(root, state="disabled")
        trim_start_seconds_entry.pack()

        trim_end_label = tk.Label(
            root, text="Please specify the end time (Make sure to add a 0 if it is a single digit. Ex: '08'):")
        trim_end_label.pack()

        trim_end_hours_label = tk.Label(root, text="hours:")
        trim_end_hours_label.pack()
        trim_end_hours_entry = tk.Entry(root, state="disabled")
        trim_end_hours_entry.pack()

        trim_end_min_label = tk.Label(root, text="minutes:")
        trim_end_min_label.pack()
        trim_end_min_entry = tk.Entry(root, state="disabled")
        trim_end_min_entry.pack()

        trim_end_seconds_label = tk.Label(root, text="seconds:")
        trim_end_seconds_label.pack()
        trim_end_seconds_entry = tk.Entry(root, state="disabled")
        trim_end_seconds_entry.pack()

        # Function to enable/disable entries based on radio button selection
        def toggle_entries():
            if trim_ans_var.get() == "yes":
                trim_start_hours_entry.config(state="normal")
                trim_start_min_entry.config(state="normal")
                trim_start_seconds_entry.config(state="normal")
                trim_end_hours_entry.config(state="normal")
                trim_end_min_entry.config(state="normal")
                trim_end_seconds_entry.config(state="normal")
            else:
                trim_start_hours_entry.config(state="disabled")
                trim_start_min_entry.config(state="disabled")
                trim_start_seconds_entry.config(state="disabled")
                trim_end_hours_entry.config(state="disabled")
                trim_end_min_entry.config(state="disabled")
                trim_end_seconds_entry.config(state="disabled")

        # Bind toggle_entries function to radio button
        trim_ans_yes.config(command=toggle_entries)
        trim_ans_no.config(command=toggle_entries)


        # Add padding
        padding_label = tk.Label(root, text="", pady=10)
        padding_label.pack()

        # DLC Parameters
        lv_label = tk.Label(
            root, text=f"Parameters For DeepLabCut - {filename}")
        lv_label.pack()

        lv_track_mouse_label = tk.Label(root, text="Do you want to track the mouse?")
        lv_track_mouse_label.pack()

        lv_track_mouse_var = tk.StringVar(value="no")
        lv_track_mouse_yes = tk.Radiobutton(
            root, text="Yes", variable=lv_track_mouse_var, value="yes")
        lv_track_mouse_no = tk.Radiobutton(
            root, text="No", variable=lv_track_mouse_var, value="no")
        lv_track_mouse_yes.pack()
        lv_track_mouse_no.pack()


        lv_ans_label = tk.Label(
            root, text="Do you want to create a labeled video?")
        lv_ans_label.pack()

        # Create radio button
        lv_ans_entry = tk.StringVar(value="no")
        lv_ans_yes = tk.Radiobutton(
            root, text="Yes", variable=lv_ans_entry, value="yes")
        lv_ans_no = tk.Radiobutton(
            root, text="No", variable=lv_ans_entry, value="no")
        lv_ans_yes.pack()
        lv_ans_no.pack()

        # Add padding
        padding_label = tk.Label(root, text="", pady=10)
        padding_label.pack()

        # DeepOf Parameters
        an_label = tk.Label(root, text=f"Parameters For DeepOF - {filename}")
        an_label.pack()

        an_ans_label = tk.Label(root, text="Do you want to analyze the files?")
        an_ans_label.pack()

        # Create radio button
        an_ans_entry = tk.StringVar(value="no")
        an_ans_yes = tk.Radiobutton(
            root, text="Yes", variable=an_ans_entry, value="yes")
        an_ans_no = tk.Radiobutton(
            root, text="No", variable=an_ans_entry, value="no")
        an_ans_yes.pack()
        an_ans_no.pack()

        distance_threshold_label = tk.Label(root, text="distance threshold:")
        distance_threshold_label.pack()
        distance_threshold_entry = tk.Entry(root, state="disabled")
        distance_threshold_entry.pack()

        time_offset_label = tk.Label(root, text="time offset:")
        time_offset_label.pack()
        time_offset_entry = tk.Entry(root, state="disabled")
        time_offset_entry.pack()

        arena_distance_label = tk.Label(
            root, text="arena_distance (NOE=500, Homecage=360):")
        arena_distance_label.pack()
        arena_distance_entry = tk.Entry(root, state="disabled")
        arena_distance_entry.pack()

        an_ans_yes.config(command=lambda: [distance_threshold_entry.config(
            state="normal"), time_offset_entry.config(state="normal"), arena_distance_entry.config(state="normal")])
        an_ans_no.config(command=lambda: [distance_threshold_entry.config(state="disabled"), time_offset_entry.config(
            state="disabled"), arena_distance_entry.config(state="disabled")])
        
        # Add padding
        padding_label = tk.Label(root, text="", pady=10)
        padding_label.pack()
        
        # LVM Files
        lvm_label = tk.Label(
            root, text=f"Parameters For LVM Demodulation - {filename}")
        lvm_label.pack()

        lvm_color_channel_label = tk.Label(
            root, text="Which color channel do you want to demodulate? (red, green, none):")
        lvm_color_channel_label.pack()

        lvm_color_channel_entry = tk.StringVar(value="none")
        lvm_color_channel_red = tk.Radiobutton(
            root, text="Red", variable=lvm_color_channel_entry, value="red")
        lvm_color_channel_green = tk.Radiobutton(
            root, text="Green", variable=lvm_color_channel_entry, value="green")
        lvm_color_channel_none = tk.Radiobutton(
            root, text="None", variable=lvm_color_channel_entry, value="none")
        lvm_color_channel_red.pack()
        lvm_color_channel_green.pack()
        lvm_color_channel_none.pack()

        #Guppy Analysis
        guppy_label = tk.Label(
            root, text=f"Parameters For Guppy Analysis - {filename}")
        guppy_label.pack()

        filter_window_label = tk.Label(
            root, text="Filter Window:")
        filter_window_label.pack()

        filter_window_entry = tk.Entry(root, validate="key", state="disabled")
        filter_window_entry.configure(validatecommand=(filter_window_entry.register(lambda s: int(s) if s.isdigit() else True), "%P"))
        filter_window_entry.pack()

        use_isosbestic_label = tk.Label(
            root, text="Use Isosbestic Channel:")
        use_isosbestic_label.pack()

        use_isosbestic = tk.StringVar(value="no")
        use_isosbestic_yes = tk.Radiobutton(
            root, text="Yes", variable=use_isosbestic, value="yes")
        use_isosbestic_no = tk.Radiobutton(
            root, text="No", variable=use_isosbestic, value="no")
        use_isosbestic_yes.pack()
        use_isosbestic_no.pack()

        window_threshold_label = tk.Label(
            root, text="Threshold Detection:")
        window_threshold_label.pack()

        window_threshold = tk.Entry(root, validate="key", state="disabled")
        window_threshold.configure(validatecommand=(window_threshold.register(lambda s: int(s) if s.isdigit() else True), "%P"))
        window_threshold.pack()

        lvm_color_channel_none.config(command=lambda: [filter_window_entry.config(state="disabled"), use_isosbestic_yes.config(state="disabled"), use_isosbestic_no.config(state="disabled"), window_threshold.config(state="disabled")])
        lvm_color_channel_green.config(command=lambda: [filter_window_entry.config(state="normal"), use_isosbestic_yes.config(state="normal"), use_isosbestic_no.config(state="normal"), window_threshold.config(state="normal")])
        lvm_color_channel_red.config(command=lambda: [filter_window_entry.config(state="normal"), use_isosbestic_yes.config(state="normal"), use_isosbestic_no.config(state="normal"), window_threshold.config(state="normal")])

        def save_parameters():
            ans = trim_ans_var.get()
            parameters["trim_start_hours"] = trim_start_hours_entry.get()
            parameters["trim_start_min"] = trim_start_min_entry.get()
            parameters["trim_start_seconds"] = trim_start_seconds_entry.get()
            parameters["trim_end_hours"] = trim_end_hours_entry.get()
            parameters["trim_end_min"] = trim_end_min_entry.get()
            parameters["trim_end_seconds"] = trim_end_seconds_entry.get()

            if ans == "yes":
                parameters["video_trimmed"] = 1
            else:
                parameters["trim_start_hours"] = 0
                parameters["trim_start_min"] = 0
                parameters["trim_start_seconds"] = 0
                parameters["trim_end_hours"] = 0
                parameters["trim_end_min"] = 0
                parameters["trim_end_seconds"] = 0
                parameters["video_trimmed"] = 0

            parameters["trim_offset"] = (int(parameters["trim_start_hours"]) * 60 * 60) + (
                int(parameters["trim_start_min"]) * 60) + int(parameters["trim_start_seconds"])

            parameters["track_mouse"] = [1 if lv_track_mouse_var.get() == "yes" else 0][0]

            parameters["labeled_video"] = [
                1 if lv_ans_entry.get() == "yes" else 0][0]

            if an_ans_entry.get() == "yes":
                parameters["analyze_files"] = 1
                parameters["distance_threshold"] = int(
                    distance_threshold_entry.get())
                parameters["time_offset"] = int(time_offset_entry.get())
                parameters["arena_distance"] = int(arena_distance_entry.get())
            else:
                parameters["analyze_files"] = 0
                parameters["distance_threshold"] = 0
                parameters["time_offset"] = 0
                parameters["arena_distance"] = 360

            parameters["lvm_color_channel"] = lvm_color_channel_entry.get()
            parameters["filter_window"] = int(filter_window_entry.get())
            parameters["use_isosbestic"] = [
                1 if use_isosbestic.get() == "yes" else 0][0]
            parameters["moving_window"] = int(window_threshold.get())
            

            parameters["objects_found"] = 0

            root.destroy()

        save_button = tk.Button(root, text="Save", command=save_parameters)
        save_button.pack()

        root.mainloop()

        return parameters

    def save_json(self, parameters, save_path):
        with open(os.path.join(save_path, "config.json"), "w") as outfile:
            json.dump(parameters, outfile, indent=4)

    def get_json(self, save_path):
        with open(os.path.join(save_path, "config.json"), 'r+') as file:
            parameters = json.load(file)

        return parameters