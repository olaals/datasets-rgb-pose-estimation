import time
import os
import numpy as np
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.widget import Widget
import cv2
import PIL
from kivy_gui import PoseInitGUI

def load_image(img_path):
    img = cv2.imread(img_path)
    img = img[:,:,:3]
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def save_image(img, img_path):
    img = convert_to_cv2(img)
    cv2.imwrite(img_path, img)

def convert_to_cv2(float_rgb_img):
    uint_img = np.uint8(float_rgb_img*254.99)
    cv2_img = cv2.cvtColor(uint_img, cv2.COLOR_RGB2BGR)
    return cv2_img

class SbButton(Button):
    def __init__(self, text="", callback=None, color=None):
        if color is None:
            super().__init__(text=text, size_hint=(1.0, None), height=30)
        else:
            super().__init__(text=text, size_hint=(1.0, None), height=30, background_color=color)
        self.callback = callback
        print("sb button")
        if(callback is not None):
            print("callback added for ", text)
            self.bind(on_press=self.cb_wrapper)

    def cb_wrapper(self,instance):
        print("cv_wrapper in sbutton")
        self.callback()

class ImageDisplay(Image):
    def __init__(self):
        super(ImageDisplay, self).__init__(size_hint=(None,None), height=100, width=100)
        self.current_frame = None
        start_img = np.zeros((320,320,3), dtype=np.uint8)
        start_img[:,:,1] = np.ones((320,320), dtype=np.uint8)*255
        w,h,c = start_img.shape
        start_img[(w//2-10):(w//2+10), (h//2-10):(h//2+10), 2] = 255
        self.update(start_img)


    def update(self, image):
        frame = image
        self.current_frame = frame
        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        #image_texture = Texture.create( colorfmt='bgr')
        #image_texture = Texture.create(colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.texture = image_texture
        print("updated image for gui")


class ImageCard(BoxLayout):
    def __init__(self, example_dict):
        super().__init__(orientation='vertical', size_hint=(None,None), height=200, width=200)
        self.image_display = ImageDisplay()
        self.add_widget(self.image_display)
        btn = Button(text="Choose", size_hint=(1.0,None), height=30)
        self.add_widget(btn)
        self.add_widget(Widget(size_hint=(None, 1.0)))
        self.add_from_dict(example_dict)

    def add_from_dict(self,example_dict):
        img_path = example_dict["img_path"]
        img = cv2.imread(img_path)
        self.image_display.update(img)

class FileChooserSidebar(BoxLayout):
    def __init__(self, mainwin_handler, ds_dict):
        #super(FileChooserSidebar, self).__init__(orientation='vertical', size_hint=(None,1.0), width=200)
        super().__init__(orientation='vertical', size_hint=(None,1.0), width=200)
        self.mainwin_handler = mainwin_handler
        self.ds_dict = ds_dict
        next_btn = SbButton("Go to next examples",self.mainwin_handler.increment_tab)
        prev_btn = SbButton("Go to prev examples",self.mainwin_handler.decrement_tab)
        self.add_widget(next_btn)
        self.add_widget(prev_btn)
        self.add_widget(Label(text="Select class", size_hint=(1.0,None), height=30))
        for key in self.ds_dict:
            btn = Button(text=key, size_hint=(1.0,None), height=30)
            btn.bind(on_press=self.change_class_callback)
            self.add_widget(btn)
        self.empty = Widget()
        self.add_widget(self.empty)

    def change_class_callback(self, instance):
        self.mainwin_handler.change_display_class(instance.text)
        
    


class HorizontalClassTab(BoxLayout):
    def __init__(self, main_win):
        super().__init__(orientation='horizontal', height=30)
        self.main_win = main_win

    def add_btn(self, name, color):
        btn = Button(text=name, background_color=color, size_hint=(1.0,None), height=30)
        btn.bind(on_press=self.btn_callback)
        self.add_widget(btn)

    def btn_callback(self, instance):
        self.main_win.change_display_class(instance.text)


class SelectFileMainWin(GridLayout):
    def __init__(self, ds_dict):
        self.rows = 6
        self.cols = 4
        self.current_tab = 0
        self.displayed_cards = []
        super().__init__(rows=self.rows, cols=self.cols, padding=10, size_hint=(1.0,1.0))
        self.ds_dict = ds_dict
        self.ds_types = []
        for key in ds_dict:
            self.ds_types.append(key)
        self.active_class = self.ds_types[0]
        self.show_imgs_for_class(self.active_class, self.current_tab)


    def get_max_number_of_tabs_for_class(self,class_type):
        examples_in_win = self.rows*self.cols
        examples = self.ds_dict[class_type]
        num_examples = len(examples)
        num_tabs = np.ceil(num_examples/examples_in_win)
        return num_tabs

        
    def show_imgs_for_class(self,class_type, tab_num):
        for displayed_card in self.displayed_cards:
            self.remove_widget(displayed_card)
        examples_in_win = self.rows*self.cols
        examples = self.ds_dict[class_type]
        num_examples = len(examples)
        num_tabs = np.ceil(50/examples_in_win)
        assert(tab_num < num_tabs)
        start_idx = tab_num*examples_in_win
        print("start_idx", start_idx)
        end_idx = start_idx + min(examples_in_win, num_examples-start_idx)
        print("end_idx", end_idx)

        for i in range(start_idx, end_idx):
            example = examples[i]
            img_card = ImageCard(example)
            self.displayed_cards.append(img_card)
            self.add_widget(img_card)

    def change_display_class(self, class_name):
        self.current_tab = 0
        self.show_imgs_for_class(class_name, self.current_tab)
        self.active_class = class_name

    def increment_tab(self):
        max_tabs = self.get_max_number_of_tabs_for_class(self.active_class)
        print("max tabs:", max_tabs)
        print("current tab:", self.current_tab)
        if(self.current_tab+1 < max_tabs):
            self.current_tab += 1
            self.show_imgs_for_class(self.active_class, self.current_tab)

    def decrement_tab(self):
        if(self.current_tab-1 >= 0):
            self.current_tab -= 1
            self.show_imgs_for_class(self.active_class, self.current_tab)


    def add_image_card(self,image_card):
        self.add_widget(image_card)

class FileChooserLayout(BoxLayout):
    def __init__(self, ds_dict, set_active_example):
        super().__init__(orientation='horizontal')
        self.ds_dict = ds_dict
        self.file_choose_mainwin = SelectFileMainWin(self.ds_dict)
        self.fc_sidebar = FileChooserSidebar(self.file_choose_mainwin, self.ds_dict)
        self.add_widget(self.fc_sidebar)
        self.add_widget(self.file_choose_mainwin)

class AppBox(BoxLayout):
    def __init__(self, ds_dict):
        super().__init__(orientation='horizontal')
        self.ds_dict = ds_dict
        self.active_layout = FileChooserLayout(self.ds_dict, self.set_active_example)
        self.add_widget(self.active_layout)

    def set_file_chooser_active(self):
        self.remove_widget(active_layout)
        self.active_layout = FileChooserLayout(self.ds_dict)
        self.add_widget(self.active_layout)

    def set_active_example(self, example_dict):
        self.remove_widget(active_layout)
        self.active_layout = PoseInitGUI(example_dict)
        self.add_widget(self.active_layout)



class PoseGUI(App):
    def __init__(self, ds_dict):
        super().__init__()
        self.ds_dict = ds_dict

    def build(self):

        print("Finished building GUI")
        return AppBox(self.ds_dict)

    def show_file_chooser(self):
        self.remove


def create_example_dict(img_path, K, gt_pose_save_path, ds_class, mesh_path, img_size, dataset_type):
    example_dict = {
            "img_path": img_path,
            "K":K,
            "gt_pose_save_path":gt_pose_save_path,
            "ds_class": ds_class,
            "dataset_type":dataset_type,
            "mesh_path": mesh_path,
            "img_size":img_size,
    }
    return example_dict

def create_real_dataset(config):
    real_ds_dict = {}

    real_dataset_path = config["real_dataset_path"]
    new_dataset_path = config["new_dataset_path"]
    ds_classes = os.listdir(real_dataset_path)
    #ds_class_paths = [os.path.join(real_dataset_path, ds_class) for ds_class in ds_classes]
    cam_mat_file = config["camera_matrix_file"]
    dataset_types = config["dataset_types"]
    img_size = config["image_size"]
    #print(ds_class_paths)
    for ds_class in ds_classes:
        real_ds_dict[ds_class] = []
        ds_class_path = os.path.join(real_dataset_path, ds_class)
        K = np.load(os.path.join(ds_class_path, cam_mat_file))
        mesh_path = os.path.join(ds_class_path, ds_class+".ply")
        for dataset_type in dataset_types:
            imgs_dir = os.path.join(ds_class_path, dataset_type)
            for idx,img_filename in enumerate(os.listdir(imgs_dir)):
                save_dir = os.path.join(new_dataset_path, ds_class, dataset_type, "ex_"+format(idx, "03d"))
                gt_pose_save_path = os.path.join(save_dir, "T_CO_gt.npy")
                os.makedirs(save_dir, exist_ok=True)
                img_path = os.path.join(imgs_dir, img_filename)
                ex_dict = create_example_dict(img_path, K, gt_pose_save_path, ds_class, mesh_path, img_size, dataset_type)
                real_ds_dict[ds_class].append(ex_dict)
    return real_ds_dict





if __name__ == '__main__':
    import sys
    sys.path.append("configs-real-datagen")
    from adapter_stiffener import get_config
    config = get_config()

    real_ds_dict = create_real_dataset(config)
    print(real_ds_dict)



    PoseGUI(real_ds_dict).run()
    pass
