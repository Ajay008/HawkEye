from tkinter import *
from modules.IndexPage import *
from modules.MD_SB import *
from modules.OT_CT import *
from modules.MD_MR import *
from modules.MD_MT import *
from modules.OT_OF import *
from modules.OT_OT import *

class App(Tk):

    color_dict = {}

    def __init__(self, *args, **kwargs):
        #loading color
        values = np.genfromtxt("data/values.csv", dtype="S" ,delimiter = '\n')
        for v in values :  
            temp = str(v).split('=')
            key  = (temp[0].strip())[2:] 
            value = (temp[1].strip())[:-1]
            self.color_dict[key] = "#"+value

        Tk.__init__(self, *args, **kwargs)
        self.title("HAWK EYE")
        self.resizable(width=False, height=False)
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}   # creating an empty list to store frames of each class
        for F in (IndexPage, MD_SB, OT_CT, MD_MR, MD_MT, OT_OF, OT_OT):     # storing frames of each class in frames
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame  
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("IndexPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        '''
        print(page)
        print(frame)
        for f in self.frames :
            print(f, self.frames[f])
        '''

app = App()
app.mainloop()