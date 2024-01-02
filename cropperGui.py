from tkinter import *
import tkinter as tk
from tkinter.ttk import *
import cv2
from PIL import ImageTk, Image
import numpy as np

class CropperGui:
    def __init__(self, image, type):
        self.master = Tk()
        self.original_image = image
        self.edited_image = self.original_image        
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.detected_object_1 = 'active'
        self.detected_object_2 = 'active'
        self.type = type
        self.detected_circles = []
        self.detected_rect = []
        self.arena_obtained = 0
        self.objects_obtained = 0
        self.object_shape = StringVar(value="circle")

        if self.type=="arena":
            self.arena_cropper()
        elif self.type=="objects":
            self.object_cropper()
        else:
            exit()
        
    def arena_cropper(self):
        self.master.attributes('-fullscreen', True)
        self.master.title('Cropper')
        
        self.frame_menu = Frame(self.master)
        self.frame_menu.pack()
        self.frame_menu.config(relief=RIDGE, padding=(50, 15))

        Label(
            self.frame_menu, text="Is the Image Cropped?").grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky='sw')

        Button(
            self.frame_menu, text="Yes", command=self.done_crop).grid(
            row=2, column=0, columnspan=2, padx=5, pady=5, sticky='sw')

        Button(
            self.frame_menu, text="Crop Image", command=self.crop_action).grid(
            row=3, column=0, columnspan=2, padx=5, pady=5, sticky='sw')
        
        Button(
            self.frame_menu, text="Auto Detect", command=self.auto_detect_arena).grid(
            row=5, column=0, columnspan=2, padx=5, pady=5, sticky='sw')

        Button(
            self.frame_menu, text="Reset Image", command=self.revert_action).grid(
                row=9, column=0, columnspan=1,padx=5, pady=5, sticky='sw')

        self.canvas = Canvas(self.frame_menu, bg="gray", width=1500, height=900)
        self.canvas.grid(row=0, column=3, rowspan=10)
        self.display_image(image=self.original_image)
        
        self.side_frame = Frame(self.frame_menu)
        self.side_frame.grid(row=0, column=4, rowspan=10)
        self.side_frame.config(relief=GROOVE, padding=(50,15))
        self.master.mainloop()

    def object_cropper(self):
        self.master.attributes('-fullscreen', True)
        self.master.title('Cropper')
        
        self.frame_menu = Frame(self.master)
        self.frame_menu.pack()
        self.frame_menu.config(relief=RIDGE, padding=(50, 15))
        self.edited_image = self.original_image.copy()

        Label(
            self.frame_menu, text="Are the objects detected correctly?").grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky='sw')

        Button(
            self.frame_menu, text="Yes", command=self.done_crop).grid(
            row=2, column=0, columnspan=2, padx=5, pady=5, sticky='sw')

        Radiobutton(
            self.frame_menu, text="Circle", variable=self.object_shape, value="circle").grid(
            row=3, column=0, columnspan=2, padx=5, pady=5, sticky='sw')

        Radiobutton(
            self.frame_menu, text="Rectangle", variable=self.object_shape, value="rectangle").grid(
            row=3, column=1, columnspan=2, padx=5, pady=5, sticky='sw')  

        Button(
            self.frame_menu, text="Select Objects", command=self.crop_action).grid(
            row=4, column=0, columnspan=2, padx=5, pady=5, sticky='sw')

        self.obj1_button = Button(
            self.frame_menu, text="Object Detected", command=self.record_object)
        self.obj1_button.grid(
            row=5, column=0, columnspan=2, padx=5, pady=5, sticky='sw')   

        self.object_label = Label(self.frame_menu, text="No Object Detected")    
        self.object_label.grid(
            row=6, column=0, columnspan=2, padx=5, pady=5, sticky='sw') 
        
        Button(
            self.frame_menu, text="Auto Detect", command=self.auto_detect_objects).grid(
            row=8, column=0, columnspan=2, padx=5, pady=5, sticky='sw')

        Button(
            self.frame_menu, text="Reset Image", command=self.revert_action).grid(
                row=9, column=0, columnspan=1,padx=5, pady=5, sticky='sw')

        self.canvas = Canvas(self.frame_menu, bg="gray", width=1500, height=900)
        self.canvas.grid(row=0, column=3, rowspan=10)
        self.display_image(image=self.original_image)
        
        self.side_frame = Frame(self.frame_menu)
        self.side_frame.grid(row=0, column=4, rowspan=10)
        self.side_frame.config(relief=GROOVE, padding=(50,15))
        self.master.mainloop()

    def record_object(self):
        if self.object_shape.get() == 'circle':
            if len(self.center) > 0:
                if [self.center[0], self.center[1], self.radius] not in self.detected_circles:
                    self.detected_circles.append([self.center[0], self.center[1], self.radius])
                    self.object_label["text"] = str(len(self.detected_circles)) + " Object Detected"
                    print(self.detected_circles)
        if self.object_shape.get() == 'rectangle':
            if self.w & self.h > 0:
                if [self.rect_xstart, self.rect_ystart, self.rect_xend, self.rect_yend] not in self.detected_rect:
                    self.detected_rect.append([self.rect_xstart, self.rect_ystart, self.rect_xend, self.rect_yend])
                    self.object_label["text"] = str(len(self.detected_rect)) + " Object Detected"  
                    print(self.detected_rect)             
                    


    def crop_action(self):
        self.rectangle_id = 0
        # self.ratio = 0
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.crop_end_x = 0
        self.crop_end_y = 0
        self.canvas.bind("<ButtonPress>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.crop)
        self.canvas.bind("<ButtonRelease>", self.end_crop)

    def start_crop(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y

    def crop(self, event):
        if self.rectangle_id:
            self.canvas.delete(self.rectangle_id)

        self.crop_end_x = event.x
        self.crop_end_y = event.y

        self.rectangle_id = self.canvas.create_rectangle(self.crop_start_x, self.crop_start_y,
                                                         self.crop_end_x, self.crop_end_y, width=1)

    def end_crop(self, event):
        if self.crop_start_x <= self.crop_end_x and self.crop_start_y <= self.crop_end_y:
            start_x = int(self.crop_start_x * self.ratio)
            start_y = int(self.crop_start_y * self.ratio)
            end_x = int(self.crop_end_x * self.ratio)
            end_y = int(self.crop_end_y * self.ratio)
        elif self.crop_start_x > self.crop_end_x and self.crop_start_y <= self.crop_end_y:
            start_x = int(self.crop_end_x * self.ratio)
            start_y = int(self.crop_start_y * self.ratio)
            end_x = int(self.crop_start_x * self.ratio)
            end_y = int(self.crop_end_y * self.ratio)
        elif self.crop_start_x <= self.crop_end_x and self.crop_start_y > self.crop_end_y:
            start_x = int(self.crop_start_x * self.ratio)
            start_y = int(self.crop_end_y * self.ratio)
            end_x = int(self.crop_end_x * self.ratio)
            end_y = int(self.crop_start_y * self.ratio)
        else:
            start_x = int(self.crop_end_x * self.ratio)
            start_y = int(self.crop_end_y * self.ratio)
            end_x = int(self.crop_start_x * self.ratio)
            end_y = int(self.crop_start_y * self.ratio)

        x = slice(start_x, end_x, 1)
        y = slice(start_y, end_y, 1)
        
        w = end_x - start_x
        h = end_y - start_y

        self.x = self.x + start_x
        self.y = self.y + start_y
        self.w = w
        self.h = h

        if self.type == "arena":
            self.edited_image = self.edited_image[y, x]
            self.display_image(self.edited_image)
        elif self.type == "objects":
            if self.object_shape.get() == "circle":
                detected_circles = self.detect_circles(self.edited_image[y, x])            
                self.center = (detected_circles[0][0] + self.x, detected_circles[0][1] + self.y)
                self.x = 0
                self.y = 0
                # circle center
                cv2.circle(self.edited_image, self.center, 1, (0, 100, 100), 3)
                # circle outline
                self.radius = detected_circles[0][2]
                cv2.circle(self.edited_image, self.center, self.radius, (255, 0, 255), 3)
                self.display_image(self.edited_image)

            elif self.object_shape.get() == "rectangle":
                self.edited_image = cv2.rectangle(self.edited_image, (start_x, start_y), (end_x, end_y), (255,0,0), 2)
                self.rect_xstart = start_x
                self.rect_ystart = start_y
                self.rect_xend = end_x
                self.rect_yend = end_y
                self.display_image(self.edited_image)
                

    def display_image(self, image=None):

        height, width = image.shape
        ratio = height / width

        new_width = width
        new_height = height

        if height > 800 or width > 1000:
            if ratio < 1:
                new_width = 1000
                new_height = int(new_width * ratio)
            else:
                new_height = 800
                new_width = int(new_height * (width / height))

        self.ratio = height / new_height
        self.new_image = cv2.resize(image, (new_width, new_height))

        self.new_image = ImageTk.PhotoImage(
            Image.fromarray(self.new_image))

        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(
            new_width / 2, new_height / 2,  image=self.new_image) 

    def done_crop(self):
        if self.type == "arena":
            if self.w == 0 or self.h == 0:
                self.arena_obtained = 0
            else:
                self.arena_obtained = 1
        if self.type == "objects":
            self.objects_obtained = 1
        self.master.destroy()    

    def auto_detect_arena(self):
        self.edited_image = self.original_image.copy()
        self.x, self.y, self.w, self.h = self.crop_arena(img=self.edited_image)
        self.display_image(image=self.original_image[self.y:self.y+self.h, self.x:self.x+self.w])

    def auto_detect_objects(self):
        self.edited_image = self.original_image.copy()
        detected_circles = self.detect_circles(self.edited_image)            
        self.obj1_button.config(state = "disabled")
        if len(detected_circles) > 2:
            detected_circles = detected_circles[:2]

        for i in detected_circles:
            center = (i[0], i[1])
            cv2.circle(self.edited_image, center, 1, (0, 100, 100), 3)
            radius = i[2]
            cv2.circle(self.edited_image, center, radius, (255, 0, 255), 3)   
        self.detected_circles = detected_circles         
        self.display_image(self.edited_image)
            

    def detect_circles(self, img_gray):
        rows = img_gray.shape[0]
        circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=100, param2=30)
        

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")

        detected_circles = []

        for i in range(len(circles)):
            if circles[i][2] > 30 & circles[i][2] < 60:
                detected_circles.append(circles[i])
        return detected_circles
        
    def revert_action(self):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.edited_image = self.original_image.copy()
        self.display_image(self.original_image)
        self.detected_circles = []
        self.detected_rect = []
        self.center = []
        self.radius = []
        if self.type == "objects":
            self.object_label["text"] = "No Object Detected"
            self.obj1_button.config(state = "enabled")

    def crop_arena(self, img, thresh_1=50, thresh_2=200):   
        # BLur image to reduce noise
        img_blur = cv2.GaussianBlur(img,(3,3), sigmaX=1, sigmaY=0)  
        
        edged = cv2.Canny(img_blur, 70, 200)
        cv2.waitKey(0)
        
        kernel = np.ones((3, 3), np.uint8)
        edged = cv2.dilate(edged, kernel, iterations=1)
        
        # Finding Contours
        # Use a copy of the image e.g. edged.copy()
        # since findContours alters the image
        contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        
        max_contours_idx = np.array([cv2.contourArea(c) for c in contours]).argmax()
        
        x, y, w, h = cv2.boundingRect(contours[max_contours_idx])
        
        return x, y, w, h                      
