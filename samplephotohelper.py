# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 11:41:37 2018
@author: Justin H Kim
1. Build Photo Frame OK
2. Add Open function OK
3. Add Save function OK
4. Build Treeview OK
5. Add Open and Load Excel function
6. Add Option Text to Photo Function
7. 
"""

# Tkinter Modules
try:
    import Tkinter as tk
    import tkFont
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk
from tkinter import filedialog    
    
# Standard Modules   
import os
import logging   
import datetime
from pprint import pprint as PRETTYPRINTTHIS    
import pandas as pd
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from PIL import ImageTk
from PIL import ImageOps
from PIL import ExifTags

class SamplePhotoHelper(tk.Tk):
    def __init__(self):
        logger = logging.getLogger(__name__)
        self.log = logging.getLogger(__name__).info
        self.bug = logging.getLogger(__name__).debug    
        super().__init__()
        
        self.waiting_add_text_pos = tk.BooleanVar()
        self.waiting_add_text_pos.set(False)
        
        self.font_size = tk.IntVar()
        self.font_size.set(15)
        
        self.font_rotate = tk.IntVar()
        self.font_rotate.set(0)        
        
        self.rename_var = tk.StringVar()
        self.rename_var.set("DefaultName")
        
        self.source_path = ""
        self.pilimage = None
        self.tkimage = None
        self._build_skeleton()
        
    def _build_skeleton(self):
        self.mainframe = tk.Frame(self)
        self.mainframe.grid(row=0,column=0,sticky="ensw")
        self.mainframe.columnconfigure(0,weight=0)
        self.mainframe.columnconfigure(1,weight=0)
        self.mainframe.rowconfigure(0,weight = 1)    
        
        self.main_photoframe, self.photocanvas = self._build_photoframe(self.mainframe)
        self.main_treeframe, self.treeview = self._build_treeframe(self.mainframe)
        
    # =========================================================================
    # PHOTOFRAME
    # =========================================================================

    def _build_photoframe(self,mainframe):
        photoframe = tk.LabelFrame(mainframe,text="Photo Window")
        photoframe.grid(row=0,column=0,padx=(20),pady=10,sticky="nw")
        photoframe.columnconfigure(0,weight=0)
        photoframe.columnconfigure(1,weight=0)
        photoframe.columnconfigure(2,weight=1)
        photoframe.columnconfigure(3,weight=1)
        photoframe.columnconfigure(4,weight=1)
        photoframe.rowconfigure(0,weight = 1)         
        
        open_photo_button = tk.Button(photoframe,text="Open Photo",
                                   command=self.open_photo)
        open_photo_button.grid(row=0,column=0,sticky="nw",padx=(10,20),pady=(10,10))
        
        save_photo_button = tk.Button(photoframe,text="Save Photo",
                                   command=self.save_photo)
        save_photo_button.grid(row=0,column=1,sticky="nw",padx=(10,10),pady=(10,10))   
        
        save_name_entry = tk.Entry(photoframe,textvariable=self.rename_var)
        save_name_entry.grid(row=0,column=2,sticky="nw",padx=(0,20),pady=(10,10))          
        
        clear_text_button = tk.Button(photoframe,text="DELETE TEXT",command=self.clear_text,
                                      foreground="red")
        clear_text_button.grid(row=0,column=4,sticky="nw",padx=(10,20),pady=(10,10))            
        
        canvas = tk.Canvas(photoframe,bg='#FFFFFF',width=450,height=600) 
        canvas.grid(row=1,column=0,sticky="nw",padx=(10,10),pady=(0,10),columnspan=5)   
        canvas.bind("<Button-1>", self.add_text_at_point)
        return photoframe, canvas    
    
    def reload_pilimage_to_canvas(self):
        self.clear_canvas(self.photocanvas)
        self.tkimage = ImageTk.PhotoImage(image=self.pilimage) 
        self.photocanvas.create_image(0, 0, image=self.tkimage, anchor="nw", tags="IMG")        

    def clear_canvas(self,canvas):
        self.log("Clearing Canvas")
        canvas.delete("all")
        canvas.update_idletasks()                 

    def toggle_wait_add_text(self):
        self.log("Adding text.")
        self.waiting_add_text_pos.set(True)
        self.photocanvas["cursor"] = "based_arrow_down"

    def add_text_at_point(self,event=None):
        if self.waiting_add_text_pos.get():
            self.photocanvas["cursor"] = "arrow"
            textx,texty = event.x,event.y
        else:
            return
        
        try:
            curr_type,curr_index,curr_id = self.get_type_index_current_item(self.treeview)
        except IndexError:
            self.bug("No treeview to get selection from.")
            return
        else:
            if curr_type == "product":
                return
            elif curr_type == "sku":
                self.log("{} - {} -{}".format(curr_type,curr_index,curr_id ))
                product_name = curr_id.split("%%")[0]
                text_str = curr_id.split("%%")[1]
            
        draw = ImageDraw.Draw(self.pilimage)
        
        fontx = ImageFont.truetype("arial.ttf", self.font_size.get())
        fonttitle = ImageFont.truetype("arial.ttf", 16)
        
        textlength,textheight = draw.textsize(text_str, font=fontx)
        coords = [(textx, texty), (textx+textlength, texty+textheight)]    
        
#        Init basic image and drawer
        
        rotate_int = self.font_rotate.get()

        txt=Image.new('RGBA', (textlength+10,textheight+8),color=(255,255,255,250))
        d = ImageDraw.Draw(txt)
        d.text((5,4), text_str, "black",font=fontx)
        txt=txt.rotate(rotate_int,  expand=1)

        self.pilimage.paste(txt,(textx, texty),mask=txt)
        
        
#        ADD PRODUCT TITLE
        if product_name not in self.rename_var.get():
            self.rename_var.set(product_name)
            textlength,textheight = draw.textsize(product_name, font=fonttitle)
            coords = [(15, 15), (15+textlength, 15+textheight)]        
            draw.rectangle(coords,fill="white")    
            draw.text((15, 15),product_name,"black",font=fontx)
            self.waiting_add_text_pos.set(False)
        
        self.clear_canvas(self.photocanvas)
        self.reload_pilimage_to_canvas()
        
    def clear_text(self):
        self.load_photo(self.source_path,self.photocanvas)
        self.reload_pilimage_to_canvas()
        
    def open_photo(self):
        self.rename_var.set("DefaultName")
        pathstr_tuple = tk.filedialog.askopenfilenames()
        path_list = list(pathstr_tuple)
        for photo_path in path_list:
            self.load_photo(photo_path, self.photocanvas)
            
    def save_photo(self):
        name = self.rename_var.get()
        ext = ".jpg"
        final_name = name + ext
        self.log("Saving photo to: {}".format(final_name))
        if self.tkimage is None:
            self.bug("No current photo in memory.")
        else:
            self.log("{}".format(type(self.tkimage)))
        self.pilimage.save("finished//"+final_name)

    def load_photo(self,path,canvas):
        self.set_pil_image_from_path(path)
        self.reload_pilimage_to_canvas()
        
    def set_pil_image_from_path(self,path):
        self.log("Setting new pilimage and tkimage vars from: {}".format(path))
        try:
            self.pilimage = Image.open(path)
        except FileNotFoundError:
            self.bug("Last path: {} no longer exists.".format(path))
            self.pilimage = None
            self.tkimage = None
        except OSError:
            self.bug("Weird error for requested image. Probably wrong selection.")
        else:
            self.source_path = path
            self.pilimage = self.resize_rotate_pilimage(self.pilimage)   
            
    def resize_rotate_pilimage(self,pilimage):
        size = 450,600
        self.log("Resizing to: {}".format(size))
        try: 
            pilimage._getexif().items()
        except AttributeError:
            self.bug("No exif data for image. Assuming portrait.")
            exif = {"Orientation": 1}
        else:
            exif=dict((ExifTags.TAGS[k], v) for k, v in pilimage._getexif().items() if k in ExifTags.TAGS)
            self.log("HEIGHT: {}, WIDTH: {}, ORIENTATION: {}".format(exif["ExifImageHeight"], exif["ExifImageWidth"],exif["Orientation"]))
        if exif['Orientation'] == 6:
            self.log("Rotating because PIL will otherwise assume this is landscape (orientation == 6)")
            pilimage=pilimage.rotate(270, expand=True)            
        pilimage = pilimage.resize(size,Image.ANTIALIAS)        
        return pilimage

    # =========================================================================
    # TREEFRAME    
    # =========================================================================
    def _build_treeframe(self,targframe):
        self.log("Building Tree Frame")
        
        tree_frame = tk.LabelFrame(self,text="Pages")
        tree_frame.grid(row=0,column=1,sticky="nsew",padx=20,pady=10)
        tree_frame.columnconfigure(0,weight=0)
        tree_frame.columnconfigure(1,weight=0)
        tree_frame.columnconfigure(2,weight=0)      
        tree_frame.columnconfigure(3,weight=0)
        tree_frame.columnconfigure(4,weight=0)      
        tree_frame.columnconfigure(5,weight=1)
#        tree_frame.columnconfigure(2,weight=1) 
        
        open_excel_button = tk.Button(tree_frame,text="Open Excel",
                                   command=self.open_excel)
        open_excel_button.grid(row=0,column=0,sticky="nw",padx=(10,20),pady=(10,10))   
        
        add_text_button = tk.Button(tree_frame,text="Add Text",command=self.toggle_wait_add_text)
        add_text_button.grid(row=0,column=1,sticky="nw",padx=(10,20),pady=(10,10))   
        
        tk.Label(tree_frame,text="Size:").grid(row=0,column=2,padx=(15,5))
        font_size_spinbox = tk.Spinbox(tree_frame, from_=10.0, to=30.0, wrap=True, 
                                       width=4,state="readonly",textvariable = self.font_size)  
        font_size_spinbox.grid(row=0,column=3,sticky="w",columnspan=1)  
        
        
        tk.Label(tree_frame,text="Rotation:").grid(row=0,column=4,padx=(15,5))
        font_rotate_spinbox = tk.Spinbox(tree_frame, from_=0, to=179.0, wrap=True, 
                                       width=4,textvariable = self.font_rotate)  
        font_rotate_spinbox.grid(row=0,column=5,sticky="w",columnspan=1)         
        
        nav_tree_cols = [("VENDOR CODE",150),("OPTION",150)]     
        nav_tree = ttk.Treeview(tree_frame, columns=[aa[0] for aa in nav_tree_cols],height=28)
        nav_tree.grid(row=1, column=0,sticky="news",pady=10,padx=10,columnspan=30)
  
        for header in nav_tree_cols:
            nav_tree.heading(header[0],text=header[0], command=lambda c=header: self.sortby(self.nav_tree, c, 0))
            nav_tree.column(header[0],width=header[1],minwidth=header[1],
                            anchor="center",stretch="true") 

        nav_tree.tag_configure("box_item",background="lightgrey")
        nav_tree.column("#0",width=150)
        nav_tree.heading("#0",text="H CODE")
                              
        nav_tree.tag_configure("product",background="#d3d3d3") 
        nav_tree.tag_configure("sku",background="#f4f4f4")
        return tree_frame,nav_tree
    
    def open_excel(self):
        pathstr = tk.filedialog.askopenfilename()
        init_df = pd.read_excel(pathstr, 0)
        required_headings = ["hcode","vendorcode","option"]
        init_df.rename(columns=lambda x: x.strip().replace( " ", "").replace("\n", "").lower(), inplace=True)
        for header in list(init_df):
            if header not in required_headings:
                init_df = init_df.drop(labels=header, axis=1)
            else:
                continue
        self.load_excel_into_treeview(init_df,self.treeview)
            
    def load_excel_into_treeview(self,df,treeview):
        used_hcodes = []
        for index, row in df.iterrows():
            hcode = row["hcode"]
            vendorcode = row["vendorcode"]
            option = row["option"]
            
            if hcode not in used_hcodes:
#                self.log("New hcode #{}: {}".format(index,hcode))
                used_hcodes.append(hcode)
                productid = treeview.insert("","end",hcode,text=hcode,tags=("product",str(index)))

            rowvals = [vendorcode,option]
            skuid = treeview.insert(productid,"end",hcode+"%%"+option,tags=("sku"),
                                    text=hcode,values=rowvals)

    def get_type_index_current_item(self,treeview):
        curItemId = treeview.selection()[0]
        if curItemId != None:
            if "product" in treeview.item(curItemId)["tags"]:
                item_tag = "product"
            elif "sku" in treeview.item(curItemId)["tags"]:
                item_tag = "sku"
            else:
                item_tag = "unknown"
            indexn = treeview.index(curItemId)
            return item_tag,indexn,curItemId
        else:
            return None          
            
            
if __name__ == "__main__":
    logname = "debug-{}.log".format(datetime.datetime.now().strftime("%y%m%d"))
    ver = "v0.0.1 - 2018/09/23"
    if not os.path.exists(r"debug\\"):
        os.mkdir(r"debug\\")
    logging.basicConfig(filename=r"debug\\{}".format(logname),
        level=logging.DEBUG, 
        format="%(asctime)s %(name)s:%(lineno)s - %(funcName)s() %(levelname)s || %(message)s",
        datefmt='%H:%M:%S')
    logging.info("-------------------------------------------------------------")
    logging.info("DEBUGLOG @ {}".format(datetime.datetime.now().strftime("%y%m%d-%H%M")))
    logging.info("VERSION: {}".format(ver))
    logging.info("AUTHOR:{}".format("Justin H Kim"))
    logging.info("-------------------------------------------------------------")
    
    app = SamplePhotoHelper()
    logging.info("App Initialized...")
    
#    app.state("zoomed")
    logging.info("App zoomed...")
    app.title("PPB Sample Photo Helper - {}".format(ver))
    logging.info("App titled...")
    app.mainloop()
    logging.info("app.mainloop() terminated.")