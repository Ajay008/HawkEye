#Common
from tkinter import *
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import cv2
import numpy as np
import threading
import math

#Specific
# Set parameters for ShiTomasi corner detection
feature_params = dict(maxCorners = 500, qualityLevel = 0.3, minDistance = 7, blockSize = 7)
# Set parameters for lucas kanade optical flow
lucas_kanade_params = dict(winSize  = (15,15), maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))


class OT_OT(Frame):
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
    prev_frame = None
    prev_gray = None
    prev_points = []
    new_points = []
    mask = None
    tracker_enabled = False
    frame = None

    click_count = 0
    top_left = (0,0)
    bottom_right = (0,0)
    frame = None
    frame_gray = None
    selected_image = None
    selected_image_gray = None
    interval = 20
    scan_count = 0
    find_keypoints_called = 0
    initial_keypoints = 0
    keypoint_accuracy = 50
    bounding_rect_accuracy = 90
    object_detection_accuracy = 80
    bounding_rect_top_left = (0,0)
    bounding_rect_bottom_right = (0,0)
    coords = []
    error = None
    draw_keypoints_enabled = False
    draw_bounding_rect_enabled = False
    mouse_x, mouse_y = 0, 0
    find_selected_image_keypoints = False
    kp2, des2 = None, None


    def __init__(self, parent, controller):

        self.bg_color = controller.color_dict['bg_color']
        self.fg_color = controller.color_dict['ot_fg_color_2']
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
        self.display.bind('<Button 1>', self.select_roi) # left click
        self.display.bind('<Motion>', self.set_mouse_motion_coords) # mouse motion    

        self.settings_panel = Frame(self, height=640, bg=self.bg_color)

        self.row=-1   #

        self.row += 1  #
        self.main_label = Label(self.settings_panel, text="Object Tracking 2", bg=self.bg_color, fg=self.fg_color, font="Times 12 bold")
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
        self.row += 1
        self.reset_selected_img_btn = Button(self.settings_panel, text="Reselect Selected image", bg=self.btn_color, command=lambda: self.reset_selected_image())
        self.reset_selected_img_btn.grid(row=self.row, column=0, columnspan=3, pady=(20,0))

        self.row +=1 
        self.draw_keypoints_checkbtn = Checkbutton(self.settings_panel, text="Show keypoints", bg=self.bg_color, fg=self.fg_color, command=lambda: self.draw_keypoints())
        self.draw_keypoints_checkbtn.grid(row=self.row, column=0, columnspan=3, sticky=W, padx=20, pady=(15,5))

        self.row +=1 
        self.draw_bounding_rect_checkbtn = Checkbutton(self.settings_panel, text="Show Bounding rectangle", bg=self.bg_color, fg=self.fg_color, command=lambda: self.draw_bounding_rect())
        self.draw_bounding_rect_checkbtn.grid(row=self.row, column=0, columnspan=3, sticky=W, padx=20, pady=(0,0))


        self.row += 1  #
        Label(self.settings_panel, text="Rectangle Accuracy : ", bg=self.bg_color, fg=self.fg_color).grid(row=self.row, column=0, pady=3)
        self.bounding_rect_accuracy_scale = Scale(self.settings_panel, from_=0, to=100, bg=self.bg_color, highlightthickness=0, orient=HORIZONTAL, length=150, sliderlength=10, command=self.change_bounding_rect_accuracy)
        self.bounding_rect_accuracy_scale.set(self.bounding_rect_accuracy)
        self.bounding_rect_accuracy_scale.grid(row=self.row, column=1, ipady=10)

        self.row += 1  #
        Label(self.settings_panel, text="Object Accuracy : ", bg=self.bg_color, fg=self.fg_color).grid(row=self.row, column=0, pady=3)
        self.obj_detection_accuracy_scale = Scale(self.settings_panel, from_=0, to=100, bg=self.bg_color, highlightthickness=0, orient=HORIZONTAL, length=150, sliderlength=10, command=self.change_object_detection_accuracy)
        self.obj_detection_accuracy_scale.set(self.bounding_rect_accuracy)
        self.obj_detection_accuracy_scale.grid(row=self.row, column=1, ipady=10)


        #Common   
        self.settings_panel.pack(side=RIGHT, fill=Y)

        #specific
        self.prev_points = np.asarray(self.prev_points, dtype=np.float32).reshape(-1,1,2)
        self.new_points = np.asarray(self.new_points, dtype=np.float32).reshape(-1,1,2)




    #Specific
    def draw_keypoints(self):
        if self.draw_keypoints_enabled == True :
            self.draw_keypoints_enabled = False
        elif self.draw_keypoints_enabled == False :
            self.draw_keypoints_enabled = True

    def draw_bounding_rect(self):
        if self.draw_bounding_rect_enabled == True :
            self.draw_bounding_rect_enabled = False
        elif self.draw_bounding_rect_enabled == False :
            self.draw_bounding_rect_enabled = True

    def change_bounding_rect_accuracy(self, value):
        self.bounding_rect_accuracy = int(value)

    def change_object_detection_accuracy(self, value) :
        self.object_detection_accuracy = int(value)

    def set_mouse_motion_coords(self, coords) :
        self.mouse_x = coords.x
        self.mouse_y = coords.y


    def select_roi(self, coords) :
        x,y = coords.x, coords.y      
        #x = np.float32(x)
        #y = np.float32(y)
        x,y  = int(x), int(y)
        
        if self.click_count < 2:
            self.click_count += 1      
            if self.click_count == 1 : 
                self.top_left = (x,y)
                self.pause()
                threading._start_new_thread(self.draw_selection_rect, ())

            elif self.click_count == 2 :
                self.bottom_right = (x,y)
                self.selected_image = self.frame[self.top_left[1]:self.bottom_right[1], self.top_left[0]:self.bottom_right[0], :]
                self.selected_image_gray = cv2.cvtColor(self.selected_image, cv2.COLOR_BGR2GRAY)
                #cv2.imshow("selected_image",self.selected_image)
                self.find_selected_image_keypoints = True
                self.find_keypoints()
                if self.error is None :
                    self.tracker_enabled = True
                self.find_selected_image_keypoints = False
                #self.error = None
                self.play()

    def draw_selection_rect(self) :
        temp_img = self.frame.copy()
        self.bottom_right = (int(self.mouse_x), int(self.mouse_y))
        #print(self.top_left, self.bottom_right)
        cv2.rectangle(temp_img, self.top_left, self.bottom_right, (255,0,0), 3)
        imgTK2 = self.convert_imgCV_to_imgTK(temp_img)         
        self.display.imgTK2 = imgTK2   # anchor imgtk so it does not be deleted by garbage-collector
        self.display.configure(image=imgTK2)
        if self.click_count == 1 :
            self.after(self.speed, self.draw_selection_rect)

    def find_keypoints(self):
        #print("find_keypoints", self.scan_count)
        surf = cv2.xfeatures2d.SURF_create(400)
        kp1,des1=surf.detectAndCompute(self.frame_gray,None)

        if self.find_selected_image_keypoints : 
            self.kp2,self.des2=surf.detectAndCompute(self.selected_image_gray,None)
            #print(des1.shape , self.des2.shape)
            #print(len(kp1), len(self.kp2))
            if len(self.kp2) < 3 :
                self.error = "No keypoints found, Try again."
                return
            else :
                self.error = None

        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1,self.des2,k=2)

        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)


        list_kp1 = []
        #list_kp2 = []
        for mat in good:
            img1_idx = mat.queryIdx
            #img2_idx = mat.trainIdx
            (x1,y1) = kp1[img1_idx].pt
            #(x2,y2) = kp2[img2_idx].pt
            list_kp1.append((x1, y1))
            #list_kp2.append((x2, y2))

        self.prev_points = []
        self.prev_points = np.asarray(self.prev_points, dtype=np.float32).reshape(-1,2)
        for (x,y) in list_kp1 :
            #cv2.circle(final_image, (int(a),int(b)), 4, (0,255,0),-1) # green
            x = np.float32(x)
            y = np.float32(y)
            self.prev_points = np.append(self.prev_points,[x,y])
        self.prev_points = self.prev_points.reshape(-1,1,2)
        #print(len(self.prev_points))


        if self.find_keypoints_called == 0 :
            self.find_keypoints_called += 1
            self.initial_keypoints = len(list_kp1)
        

    def find_bounding_rect_coords(self):
        coords_count = self.coords.shape[0]
        #print(coords_count)
        coords_x = [x for x,y in self.coords]
        coords_y = [y for x,y in self.coords]
        left = min(coords_x)
        right = max(coords_x)
        top = min(coords_y)
        bottom = max(coords_y)

        tolerance = coords_count * (100-self.bounding_rect_accuracy)/100
        while left < 640 :
            left += 10 
            #print("1 ", left)
            temp = [x for x,y in self.coords if x<left]
            if len(temp) > tolerance :
                #left = min([x for x,y in self.coords if x>left-10 and x<left])
                #print(temp, max(temp))
                temp = [x for x,y in self.coords if x<left+10]
                left = max(temp)
                #print("2 ", left)
                break
        
        while right > 0 :
            right -= 10 
            temp = [x for x,y in self.coords if x>right]
            if len(temp) > tolerance :
                #right = min([x for x,y in self.coords if x<right+10 and x>right])
                temp = [x for x,y in self.coords if x>right-10]
                right = min(temp)
                break
        while top < 480 :
            top += 10 
            temp = [y for x,y in self.coords if y<top]
            if len(temp) > tolerance :
                #top = min([y for x,y in self.coords if y>top-10 and y<top])
                temp = [y for x,y in self.coords if y<top+10]
                top = max(temp)
                break
        while bottom > 0 :
            bottom -= 10 
            temp = [y for x,y in self.coords if y>bottom]
            if len(temp) > tolerance :
                #bottom = min([y for x,y in self.coords if y<bottom+10 and y>bottom])
                temp = [y for x,y in self.coords if y>bottom-10]
                bottom = min(temp)
                break
        self.bounding_rect_top_left = (int(left), int(top))
        self.bounding_rect_bottom_right = (int(right), int(bottom))
        
        

        

    def object_tracking(self):
        self.scan_count += 1 
        self.prev_points = self.prev_points.reshape(-1,1,2)   
        self.frame_gray = self.resize_image(self.frame_gray)
        self.new_points, status, errors = cv2.calcOpticalFlowPyrLK(self.prev_gray, self.frame_gray, self.prev_points, None, **lucas_kanade_params)
        
        #avg_x, avg_y = 0, 0
        if self.new_points is not None: 
            temp = self.new_points[status==1]
            self.coords = temp.reshape(-1,2)
            for x,y in self.coords:
                #avg_x += x
                #avg_y += y
                if self.draw_keypoints_enabled : 
                    cv2.circle(self.frame, (int(x),int(y)), 3, (0,255,0),-1)

            if len(self.coords) >= self.initial_keypoints * (100-self.object_detection_accuracy)/100 :            
                if self.draw_bounding_rect_enabled : 
                    if len(self.coords) != 0 :
                        self.find_bounding_rect_coords()
                        cv2.rectangle(self.frame, self.bounding_rect_top_left , self.bounding_rect_bottom_right, (255,0,0), 2)
                '''
                avg_x /= len(self.coords)
                avg_y /= len(self.coords)
                avg_x, avg_y = int(avg_x), int(avg_y)

                cv2.line(self.frame,(avg_x-10 ,avg_y),(avg_x+10 ,avg_y),(255,0,0),2)
                cv2.line(self.frame,(avg_x ,avg_y-10),(avg_x ,avg_y+10),(255,0,0),2)
                cv2.circle(self.frame, (avg_x, avg_y), 15, (255,0,0), 2)
                '''
            
                coords_x_30 = [0] * (math.ceil(640/30) + 1)
                coords_y_30 = [0] * (math.ceil(480/30) + 1)
                for x,y in self.coords :
                    i, j = int(x/30), int(y/30)
                    coords_x_30[i] += 1
                    coords_y_30[j] += 1
                center_x = coords_x_30.index(max(coords_x_30)) * 30 + 15
                center_y = coords_y_30.index(max(coords_y_30)) * 30 + 15

                cv2.line(self.frame,(center_x-10 ,center_y),(center_x+10 ,center_y),(255,0,0),2)
                cv2.line(self.frame,(center_x ,center_y-10),(center_x ,center_y+10),(255,0,0),2)
                cv2.circle(self.frame, (center_x, center_y), 15, (255,0,0), 2)
            else : 
                cv2.putText(self.frame,"Object Not Found",(0,20),cv2.FONT_HERSHEY_SIMPLEX,1,color = (200,50,75),thickness = 3)

            self.prev_gray = self.frame_gray.copy()
            self.prev_points = self.new_points.reshape(-1,1,2)
        
        else : 
            cv2.putText(self.frame,"Object Not Found",(0,20),cv2.FONT_HERSHEY_SIMPLEX,1,color = (200,50,75),thickness = 3)

            
        cond_1 = self.new_points is None
        cond_2 = self.prev_points[status==1].shape[0] < self.initial_keypoints * self.keypoint_accuracy/100
        cond_3 = self.scan_count % self.interval == 0
        if cond_1 or cond_2 or cond_3 :
            #threading._start_new_thread(self.find_keypoints, ())
            self.find_keypoints()
            self.error = None
        if self.scan_count == 500 :
            self.scan_count == 0
    






    def reset_selected_image(self):
        self.click_count = 0
        self.tracker_enabled = False
        self.error = None



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

            #specific
            _, self.prev_frame = self.cap.read()
            self.prev_gray = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY)
            self.prev_gray = self.resize_image(self.prev_gray)

        self.paused = False
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.play()

    def play(self):
        #print("playing")
        available, self.frame = self.cap.read()
        self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        if available :
            self.frame = self.resize_image(self.frame)

            if self.tracker_enabled : 
                self.object_tracking()
            elif self.error is not None : 
                cv2.putText(self.frame,self.error,(0,20),cv2.FONT_HERSHEY_SIMPLEX,1,color = (200,50,75),thickness = 3)

            imgTK2 = self.convert_imgCV_to_imgTK(self.frame)         

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
            #print("relesed")
        controller.show_frame("IndexPage")
        