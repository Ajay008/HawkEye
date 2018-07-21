from modules.MD_SB import *
from modules.OT_CT import *
from tkinter import *

class IndexPage(Frame):    
    #bg_color="#333333"
    bg_color = "black"

    md = None
    ct = None
    ot = None
    mr = None
    of = None
    mt = None

    md_fg_color = None
    md_fg_color = None
    ct_fg_color = None
    mr_fg_color = None
    mt_fg_color = None
    of_fg_color = None
    ot_fg_color = None


    md_fg_color_2 = None
    ct_fg_color_2 = None
    mr_fg_color_2 = None
    mt_fg_color_2 = None
    of_fg_color_2 = None
    ot_fg_color_2 = None

    def __init__(self, parent, controller):  
        Frame.__init__(self, parent, bg=self.bg_color)
        self.controller = controller
        controller.config(bg=self.bg_color)

        self.md_fg_color = controller.color_dict['md_fg_color']
        self.ct_fg_color = controller.color_dict['ct_fg_color']
        self.mr_fg_color = controller.color_dict['mr_fg_color']
        self.mt_fg_color = controller.color_dict['mt_fg_color']
        self.of_fg_color = controller.color_dict['of_fg_color']
        self.ot_fg_color = controller.color_dict['ot_fg_color']

        self.md_fg_color_2 = controller.color_dict['md_fg_color_2']
        self.ct_fg_color_2 = controller.color_dict['ct_fg_color_2']
        self.mr_fg_color_2 = controller.color_dict['mr_fg_color_2']
        self.mt_fg_color_2 = controller.color_dict['mt_fg_color_2']
        self.of_fg_color_2 = controller.color_dict['of_fg_color_2']
        self.ot_fg_color_2 = controller.color_dict['ot_fg_color_2']



        #for i in range(10) : 
         #       Label(self, text="", width=5, height=1, bg=self.bg_color).grid(row=0, column=i, padx=2)
        

        logo_img = PhotoImage(file="images/center_img.png")
        logo = Label(self, image=logo_img, borderwidth=0)
        logo.image = logo_img
        logo.grid(row=1, column=1, padx=(0,0))

        
        self.md = Label(self, text="Motion Detection", fg=self.md_fg_color,  font="Times 22 bold italic", bg=self.bg_color, borderwidth=0)
        self.md.bind('<Button-1>', lambda event, page_name="MD_SB": controller.show_frame(page_name))
        self.md.bind('<Enter>', lambda event, widget_name="md" : self.on_mouse_enter(widget_name))
        self.md.bind('<Leave>', lambda event, widget_name="md" : self.on_mouse_leave(widget_name))
        self.md.grid(row=0, column=0, padx=(140,0), pady=(60,0), sticky=E)
        
        '''
        ct = Button(self, text="Color Tracker", fg="green",  font="Times 22 bold italic", bg=self.bg_color, command=lambda: controller.show_frame("OT_CT"), borderwidth=0)
        ct.grid(row=5, column=1, padx=20, pady=20)
        '''
        
        self.ct = Label(self, text="Color Tracker", fg=self.ct_fg_color,  font="Times 22 bold italic", bg=self.bg_color, borderwidth=0)
        self.ct.bind('<Button-1>', lambda event, page_name="OT_CT": controller.show_frame(page_name))
        self.ct.bind('<Enter>', lambda event, widget_name="ct" : self.on_mouse_enter(widget_name))
        self.ct.bind('<Leave>', lambda event, widget_name="ct" : self.on_mouse_leave(widget_name))
        self.ct.grid(row=0, column=2, padx=(0,0), pady=(60,0), sticky=W)
        

        self.mr = Button(self, text="Motion Recorder", fg=self.mr_fg_color,  font="Times 22 bold italic", bg=self.bg_color, borderwidth=0)
        self.mr.bind('<Button-1>', lambda event, page_name="MD_MR": controller.show_frame(page_name))
        self.mr.bind('<Enter>', lambda event, widget_name="mr" : self.on_mouse_enter(widget_name))
        self.mr.bind('<Leave>', lambda event, widget_name="mr" : self.on_mouse_leave(widget_name))
        self.mr.grid(row=1, column=0, padx=(70,70), pady=0)

        self.mt = Button(self, text="Motion Tracker", fg=self.mt_fg_color,  font="Times 22 bold italic", bg=self.bg_color, borderwidth=0)
        self.mt.bind('<Button-1>', lambda event, page_name="MD_MT": controller.show_frame(page_name))
        self.mt.bind('<Enter>', lambda event, widget_name="mt" : self.on_mouse_enter(widget_name))
        self.mt.bind('<Leave>', lambda event, widget_name="mt" : self.on_mouse_leave(widget_name))
        self.mt.grid(row=1, column=2, padx=(70,0), pady=0)

        self.of = Button(self, text="Object Tracking 1", fg=self.of_fg_color,  font="Times 22 bold italic", bg=self.bg_color, borderwidth=0)
        self.of.bind('<Button-1>', lambda event, page_name="OT_OF": controller.show_frame(page_name))
        self.of.bind('<Enter>', lambda event, widget_name="of" : self.on_mouse_enter(widget_name))
        self.of.bind('<Leave>', lambda event, widget_name="of" : self.on_mouse_leave(widget_name))
        self.of.grid(row=2, column=0, padx=(140,0), pady=0, sticky=E)

        self.ot = Button(self, text="Object Tracking 2", fg=self.ot_fg_color,  font="Times 22 bold italic", bg=self.bg_color, borderwidth=0)
        self.ot.bind('<Button-1>', lambda event, page_name="OT_OT": controller.show_frame(page_name))
        self.ot.bind('<Enter>', lambda event, widget_name="ot" : self.on_mouse_enter(widget_name))
        self.ot.bind('<Leave>', lambda event, widget_name="ot" : self.on_mouse_leave(widget_name))
        self.ot.grid(row=2, column=2, padx=0, pady=0, sticky=W)

    def on_mouse_enter(self, widget_name):
        if widget_name == "md" :
            self.md.configure(fg=self.md_fg_color_2)
        elif widget_name == "ct" :
            self.ct.configure(fg=self.ct_fg_color_2)
        elif widget_name == "mr" :
            self.mr.configure(fg=self.mr_fg_color_2)
        elif widget_name == "mt" :
            self.mt.configure(fg=self.mt_fg_color_2)
        elif widget_name == "of" :
            self.of.configure(fg=self.of_fg_color_2)
        elif widget_name == "ot" :
            self.ot.configure(fg=self.ot_fg_color_2)

    def on_mouse_leave(self, widget_name):
        if widget_name == "md" :
            self.md.configure(fg=self.md_fg_color)
        elif widget_name == "ct" :
            self.ct.configure(fg=self.ct_fg_color)
        elif widget_name == "mr" :
            self.mr.configure(fg=self.mr_fg_color)
        elif widget_name == "mt" :
            self.mt.configure(fg=self.mt_fg_color)
        elif widget_name == "of" :
            self.of.configure(fg=self.of_fg_color)
        elif widget_name == "ot" :
            self.ot.configure(fg=self.ot_fg_color)


        