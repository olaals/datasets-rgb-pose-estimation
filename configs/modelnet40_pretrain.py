import torch
import os


all_classes_modelnet40 = ["airplane", "bench", "bowl", "cone", "desk", "flower_pot", "keyboard", "mantel", "person", "radio",
                          "sofa", "table", "tv_stand", "xbox", "bathtub", "bookshelf", "car", "cup", "door", "glass_box",
                          "lamp", "monitor", "piano", "range_hood", "stairs", "tent", "vase", "bed", "bottle", "chair", "curtain",
                          "dresser", "guitar", "laptop", "night_stand", "plant", "sink", "stool", "toilet", "wardrobe"]



def get_config():

    this_file_name = os.path.split(os.path.splitext(__file__)[0])[-1]
    print("Config file name:", this_file_name)




    return {
        "config_name":this_file_name,
        "general":{
            "modelnet_classes": ["airplane"], # all_classes or specify indivudal as ["desk", "sofa", "plant"]
            "num_sample_vertices": 1000,  # number of vertices sampled from the mesh
            "dataset_name": "ModelNet40-norm-ply",
            "split":{
                "train":8000,
                "validation": 2000,
                "test": 1000,
            },

        },
        "renderer":{
            "ground_truth": {
                "name":"mitsuba", # pyrender or mitsuba
                "material_sampler": {
                    "type":"metal",
                },
                "samples":512,
                "path_depth":4,
            },
            "guess": {
                "name":"pyrender", # mitsuba, pyrender or none
            }
        },
        "camera_intrinsics":{
            "focal_length": 50, #mm
            "sensor_width": 36, #mm
            "image_resolution": 300, # width=height
        },
        "scene_config":{
            "distance_cam_to_world": 1.8, #meters
            "distance_cam_to_world_deviation":0.1, #meters
            "world_to_object_gt_transl_deviation": 0.1, #meters
            "world_to_object_transl_deviation": 0.1, #meters
            "world_to_object_angle_deviation":25, #degrees
        },
    }


if __name__ == '__main__':
    config = get_config()
    for param_dict_key in config:
        param_dict = config[param_dict_key]
        print("")
        print(param_dict_key.upper())
        if(type(param_dict) is dict):
            for key in param_dict:
                value = param_dict[key]
                print(key, ":", value)


