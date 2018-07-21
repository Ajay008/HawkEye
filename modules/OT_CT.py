#Common
from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np
import threading

#Specific


class OT_CT(Frame):
    #Common
    path = 0
    cap = None    
    display = None
    paused = True
    released = True
    speed = 1   # higher the value lesser the playing speed (only integer value allowed)
    bg_color = None
    fg_color = None
    btn_color = None
    row=0

    #Specific
    selected_color_image = None    
    color_lower_range = (0,100,100)
    color_higher_range = (179,255,255)
    color_tracker_activated = False
    hue_tolerance_scale = None
    hue_tolerance = 5
    h_int, s_int, v_int = 0,0,0

    def __init__(self, parent, controller):

        self.bg_color = controller.color_dict['bg_color']
        self.fg_color = controller.color_dict['ct_fg_color']
        self.btn_color = self.fg_color

        #Common
        Frame.__init__(self, parent)
        self.controller = controller
 
        self.img_black = np.zeros((480,640,3), np.uint8)
        self.img_black_TK = self.convert_imgCV_to_imgTK(self.img_black)

        self.display_frame = Frame(self, width=480, height=640)
        self.display = Label(self.display_frame,image=self.img_black_TK)
        #self.display.image = tmpImg
        self.display.pack()
        self.display_frame.pack(side=LEFT, fill=Y)
        #specific
        self.display.bind('<Button 1>', self.getCoords)



        self.settings_panel = Frame(self, height=640, bg=self.bg_color)

        self.row=-1   #

        self.row += 1  #
        self.main_label = Label(self.settings_panel, text="Color Tracker", bg=self.bg_color, fg=self.fg_color, font="Times 12 bold")
        self.main_label.grid(row=self.row, column=0, columnspan=2)

        self.back_btn_image = PhotoImage(file="images/back.png")
        self.back_btn = Button(self.settings_panel, image=self.back_btn_image, bg=self.btn_color, width=30, command=lambda: self.goBack(controller))
        self.back_btn.grid(row=self.row, column=2, padx=10, pady= (5,2), sticky=N)
        self.back_btn.image = self.back_btn_image
        
        self.row += 1  #
        self.blank_space = Frame(self.settings_panel, height=3, width=330, bg=self.fg_color)
        self.blank_space.grid(row=self.row, column=0, columnspan=3)

        self.row += 1   #
        self.btn_container = Label(self.settings_panel, bg=self.bg_color)
        self.btn_container.grid(row=self.row, column=0, columnspan=3, pady=10)

        self.start_btn_image = PhotoImage(file="images/play.png")
        self.start_btn = Button(self.btn_container, image=self.start_btn_image, bg=self.btn_color, command=lambda: self.start())
        self.start_btn.grid(row=0, column=0)
        self.start_btn.image = self.start_btn_image
        
        self.pause_btn_image = PhotoImage(file="images/pause.png")
        self.pause_btn = Button(self.btn_container, state="disabled", image=self.pause_btn_image, bg=self.btn_color, command=lambda: self.pause())
        self.pause_btn.grid(row=0, column=1, padx=10)
        self.pause_btn.image = self.pause_btn_image

        self.row += 1  #
        self.path_label = Label(self.settings_panel, text="Enter path of video :", font="Times 10 bold", bg=self.bg_color, fg=self.fg_color)
        self.path_label.grid(row=self.row, column=0, columnspan=3, sticky=W, padx=10)

        self.row += 1  #
        self.enter_path = Entry(self.settings_panel, width=40)
        self.enter_path.grid(row=self.row, column=0, columnspan=2, sticky=W, padx=20)
        self.enter_path.bind("<Return>",self.load_video)

        self.browse_path_btn = Button(self.settings_panel, text="Browse", bg=self.btn_color, command=lambda: self.browse())
        self.browse_path_btn.grid(row=self.row, column=2)

        self.row += 1 #
        self.path_note = Label(self.settings_panel, text="Note: Enter 0 for Webcam.", font="Times 6 bold", bg=self.bg_color, fg=self.fg_color)
        self.path_note.grid(row=self.row, column=0, columnspan=3, sticky=W, padx=20, pady=(0,20))

        #specific
        self.row += 1 #
        self.selected_color_display = Label(self.settings_panel, text="",  width=2, bg=self.bg_color) 
        self.selected_color_display.grid(row=self.row, column=0, pady=(0,20), padx=0)

        self.start_tracking_btn = Button(self.settings_panel, text="Start Tracking", state="disabled", bg=self.btn_color, command=lambda: self.start_tracking())
        self.start_tracking_btn.grid(row=self.row, column=0, padx=0, columnspan=2, pady=(0,20))

        self.row += 1  #
        self.blank_space = Frame(self.settings_panel, height=1, width=280, bg=self.fg_color)
        self.blank_space.grid(row=self.row, column=0, columnspan=3)
        
        self.row += 1  #
        self.additional_settings = Label(self.settings_panel, text="Additional Settings", bg=self.bg_color, fg=self.fg_color, font="Times 14 bold")
        self.additional_settings.grid(row=self.row, column=0, columnspan=3)
        
        self.row += 1  #
        self.blank_space = Frame(self.settings_panel, height=1, width=280, bg=self.fg_color)
        self.blank_space.grid(row=self.row, column=0, columnspan=3, pady=(0,10))


        #Specific
        
        self.row += 1  #
        Label(self.settings_panel, text="Hue Tolerance : ", bg=self.bg_color, fg=self.fg_color).grid(row=self.row, column=0)
        self.hue_tolerance_scale = Scale(self.settings_panel, from_=0, to=50, bg=self.bg_color, highlightthickness=0, orient=HORIZONTAL, length=150, sliderlength=10, command=self.change_hue_tolerance)
        self.hue_tolerance_scale.set(self.hue_tolerance)
        self.hue_tolerance_scale.grid(row=self.row, column=1, ipady=7)





        #Common   
        self.settings_panel.pack(side=RIGHT, fill=Y)

    #Specific
    def getCoords(self, coords):
        #print("coords : ", coords.y, coords.x)   
        if self.selected_color_image is not None: 
            b,g,r = self.selected_color_image[coords.y][coords.x]
            hex_r = str(hex(r))[2:]
            hex_g = str(hex(g))[2:] 
            hex_b = str(hex(b))[2:]
            if len(hex_b) == 1 :
                hex_b = "0" + hex_b
            if len(hex_g) == 1 :
                hex_g = "0" + hex_g
            if len(hex_r) == 1 :
                hex_r = "0" + hex_r
            temp_color = "#" + hex_r + hex_g + hex_b
            print(temp_color)
            self.selected_color_display.config(bg=temp_color)

            image_hsv = cv2.cvtColor(self.selected_color_image, cv2.COLOR_BGR2HSV)
            h,s,v = image_hsv[coords.y,coords.x]
            print(image_hsv[coords.y,coords.x])
            self.h_int, self.s_int, self.v_int = int(h), int(s), int(v)
            
            if not self.color_tracker_activated :
                self.start_tracking_btn.config(state="normal") 

    def start_tracking(self):
        self.color_tracker_activated = True
        self.start_tracking_btn.config(state="disabled") 
        self.paused = False
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.play()
        self.pause()
        self.play()

        #self.released = True
        #self.start()
        '''
        if self.cap :
            self.paused = True
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.cap.release()
            self.released = True
            print("relesed")
            self.color_tracker_activated = True
            self.start_tracking_btn.config(state="disabled")
            self.start()
        '''

    def color_tracker(self, image):        

        h_low = self.h_int - self.hue_tolerance
        h_high = self.h_int + self.hue_tolerance
        if h_low < 0 :
            h_low = 0
        if h_high > 179 : 
            h_high = 179

        s_low = self.s_int - 10
        s_high = self.s_int + 10
        if s_low < 0 :
            s_low = 0
        if s_high > 255 : 
            s_high = 255

        v_low = self.v_int - 15
        v_high = self.v_int + 15
        if v_low < 0 :
            v_low = 0
        if v_high > 255 : 
            v_high = 255

        self.color_lower_range = (h_low,100,100)
        self.color_higher_range = (h_high,255,255)

        if self.s_int < 100 :
            self.color_lower_range = (h_low,s_low,100)
            self.color_higher_range = (h_high,s_high,255)
        if self.v_int < 100 :
            self.color_lower_range = (h_low,100,v_low)
            self.color_higher_range = (h_high,255,v_high)
        if self.s_int<100 and self.v_int<100 : 
            self.color_lower_range = (h_low,s_low,v_low)
            self.color_higher_range = (h_high,s_high,v_high)        



        image_hsv2 = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(image_hsv2, self.color_lower_range, self.color_higher_range)
        mask = cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)
        #frame_and = cv2.bitwise_and(image, image, mask=mask)
        #cv2.imshow("colorFilter",frame_and)   
    
        blur = cv2.GaussianBlur(mask,(3,3),0)
        #blur = cv2.GaussianBlur(frame_and,(3,3),0)
        #blur = cv2.medianBlur(frame_and,7)
        #cv2.imshow("blur",blur)       
    
        gray = cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)
        #cv2.imshow("gray",gray)   
    
        edged = cv2.Canny(gray, 30, 200)
        #cv2.imshow("edged",edged)   
    
        img2, contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image, contours, -1, (0,255,0), 3)
        #cv2.imshow('colorTracker', frame2)
        return image

    def change_hue_tolerance(self, value):
        self.hue_tolerance = int(value)



    #Common
    def browse(self):
        self.path = filedialog.askopenfilename(initialdir="/", title="select a video file", filetypes = (("Video files",("*.mp4","*.avi")),("All files","*.*")))
        self.enter_path.delete(0, END)
        self.enter_path.insert(0, self.path)
        if not self.path:
            self.path = 0
            self.enter_path.insert(0,"0")
        self.load_video("temp")

    def load_video(self, temp):
        self.path = self.enter_path.get()
        if self.path == "0":
            self.path = int(self.path)
        if self.cap : 
            self.cap.release()
            self.released = True
            print("relesed")
            self.paused = True
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.color_tracker_activated = False
        self.start()

    def resize_image(self,img):
        img_shape = img.shape
        img_height = img_shape[0]
        img_width = img_shape[1]
            
        img_resized = img

        if img_height > 480 :
            ratio_height =  480 / img_height
            ratio_width = 640 / img_width
            img_resized = cv2.resize(img, None, fx=ratio_width, fy=ratio_height, interpolation= cv2.INTER_AREA)
        elif img_height < 480 :
            img_resized = cv2.resize(img, (640,480), interpolation= cv2.INTER_CUBIC)

        '''
        if (img_resized.shape[0] != 480 or img_resized[1] != 640).any() :
            img_resized =  cv2.resize(img_resized, (640,480), interpolation= cv2.INTER_CUBIC)
        '''
        #print(img.shape)
        #print(img_resized.shape)
        return img_resized

    def convert_imgCV_to_imgTK(self, imgCV):
        imgCV2 = cv2.cvtColor(imgCV,cv2.COLOR_BGR2RGB)
        imgTK = Image.fromarray(imgCV2)
        imgTK2 = ImageTk.PhotoImage(image=imgTK)
        return imgTK2

    def start(self):
        #print("starting")
        #print(self.cap, self.path)
        if self.released : 
            self.cap = cv2.VideoCapture(self.path)
            self.released = False
            #print(self.cap, self.path)
        self.paused = False
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.play()

    def play(self):
        #print("playing")
        available, imgCV = self.cap.read()
        if available :
            #print("available")
            imgCV_resized = self.resize_image(imgCV)
            self.selected_color_image = imgCV_resized

            if self.color_tracker_activated : 
                imgCV_resized = self.color_tracker(imgCV_resized)
            #threading._start_new_thread(self.motion_detection, ("t1", imgCV_resized))

            imgTK2 = self.convert_imgCV_to_imgTK(imgCV_resized)         

            self.display.imgTK2 = imgTK2   # anchor imgtk so it does not be deleted by garbage-collector
            self.display.configure(image=imgTK2)   
        if not self.paused :
            self.after(self.speed, self.play)

    def pause(self):
        self.paused = True
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")

    def goBack(self, controller):
        self.paused = True
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        if self.cap:
            self.cap.release()
            self.released = True
            print("relesed")
        controller.show_frame("IndexPage")
        
