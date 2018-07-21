#Common
from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np
import threading

#Specific
import winsound

class MD_SB(Frame):
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
    subtractor = cv2.createBackgroundSubtractorMOG2()
    hist_threshold = 5000    # motion sensitivity => higher the value lesser the sensitivity
    motion_sensivity_scale = None
    alaram_freq_scale = None
    #noise_value = 0
    alaram_frequency = 100

    def __init__(self, parent, controller):

        self.bg_color = controller.color_dict['bg_color']
        self.fg_color = controller.color_dict['md_fg_color']
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

        self.settings_panel = Frame(self, height=640, bg=self.bg_color)

        self.row=-1   #

        self.row += 1  #
        self.main_label = Label(self.settings_panel, text="Motion Detection", bg=self.bg_color, fg=self.fg_color, font="Times 12 bold")
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
        self.path_note.grid(row=self.row, column=0, columnspan=3, sticky=W, padx=20, pady=(0,30))

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
        Label(self.settings_panel, text="Motion sensitivity : ", bg=self.bg_color, fg=self.fg_color).grid(row=self.row, column=0, pady=3)
        self.motion_sensivity_scale = Scale(self.settings_panel, from_=0, to=50000, bg=self.bg_color, highlightthickness=0, orient=HORIZONTAL, length=150, sliderlength=10, command=self.change_hist_threshold)
        self.motion_sensivity_scale.set(self.hist_threshold)
        self.motion_sensivity_scale.grid(row=self.row, column=1, ipady=10)
        
        self.row += 1  #
        Label(self.settings_panel, text="Alaram frequency : ", bg=self.bg_color, fg=self.fg_color).grid(row=self.row, column=0)
        self.alaram_freq_scale = Scale(self.settings_panel, from_=37, to=6000, bg=self.bg_color, highlightthickness=0, orient=HORIZONTAL, length=150, sliderlength=10, command=self.change_alaram_frequency)
        self.alaram_freq_scale.set(self.alaram_frequency)
        self.alaram_freq_scale.grid(row=self.row, column=1, ipady=7)

        #Common   
        self.settings_panel.pack(side=RIGHT, fill=Y)

    #Specific
    def motion_detection(self, temp, img):
        blur = cv2.GaussianBlur(img, (19,19), 0)
        mask = self.subtractor.apply(blur)
        img_temp = np.ones(img.shape, dtype="uint8") * 255
        img_temp_and = cv2.bitwise_and(img_temp, img_temp, mask=mask)
        img_temp_and_bgr = cv2.cvtColor(img_temp_and, cv2.COLOR_BGR2GRAY)

        hist, bins = np.histogram(img_temp_and_bgr.ravel(), 256, [0,256])
        #print(hist[255])

        if hist[255] > self.hist_threshold :
            #winsound.Beep(self.alaram_frequency, 10)
            threading._start_new_thread(winsound.Beep, (self.alaram_frequency, 20))
            

    def change_hist_threshold(self, value):
        self.hist_threshold = int(value)

    def change_alaram_frequency(self, value):
        self.alaram_frequency = int(value)








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
        self.released = True
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

            self.motion_detection("t1",imgCV_resized)
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
        