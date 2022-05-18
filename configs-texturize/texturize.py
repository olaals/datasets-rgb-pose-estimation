import os


all_classes_modelnet10 = ["bathtub", "bed", "chair", "desk", "dresser", "monitor", "night_stand", "sofa", "table", "toilet"]

all_texture_classes = ["banded","blotchy","braided","bubbly","bumpy","chequered",
                   "cobwebbed","cracked","crosshatched","crystalline","dotted",
                   "fibrous","flecked","freckled","frilly","gauzy","grid","grooved",
                   "honeycombed","interlaced","knitted","lacelike","lined","marbled",
                   "matted","meshed","paisley","perforated","pitted","pleated",
                   "polka-dotted","porous","potholed","scaly","smeared","spiralled",
                   "sprinkled","stained","stratified","striped","studded","swirly",
                   "veined","waffled","woven","wrinkled","zigzagged"]



def get_config():

    this_file_name = os.path.split(os.path.splitext(__file__)[0])[-1]
    print("Config file name:", this_file_name)
    return {
        "config_name":this_file_name,
        "modelnet_classes": all_classes_modelnet10, # all_classes or specify indivudal as ["desk", "sofa", "plant"]
        "texture_classes": all_texture_classes,
        "blender_exec_path":"/home/ola/library/blender312/blender",

    }

