import os
from conf_helpers import *

all_classes_modelnet10 = ["bed", "chair", "desk", "dresser", "monitor", "night_stand", "sofa", "table", "toilet"]

def get_config():

    this_file_name = os.path.split(os.path.splitext(__file__)[0])[-1]
    print("Config file name:", this_file_name)




    return {
        "config_name":this_file_name,
        "general":{
            "modelnet_classes": all_classes_modelnet10, # all_classes or specify indivudal as ["desk", "sofa", "plant"]
            "num_sample_vertices": 1000,  # number of vertices sampled from the mesh
            "dataset_name": "ModelNet10-norm-clean-ply",
            "split":{
                "train":25000,
                "validation": 100,
                "test": 100,
            },

        },
        "real_render": {
             "name":"blender", # pyrender or mitsuba
             "env_map_types": ["industrial-4k"], # list or constant
             "exec_path":"/home/ola/library/blender312/blender",
             "py_script_path":"blender-cache/script.py",
             "cache_dir":"blender-cache",
             "nested_pyrender": None,
             "env_map_multiplier": (1.0, 1.3),
             "material_samplers": [blender_pbr_sampler("metal", 0.5, (0.1,0.7)), blender_metal_sampler(0.5, (0.2,0.3), (0.2,0.4))],
         },
        "guess_render": pyrender_conf(True,True),
        "camera_intrinsics":{
            "focal_length": 50, #mm
            "sensor_width": 36, #mm
            "image_resolution": 720, # width=height
        },
        "scene_config":{
            "distance_cam_to_world": 2.8, #meters
            "distance_cam_to_world_deviation":0.2, #meters
            "world_to_object_gt_transl_deviation": 0.05, #meters
            "world_to_object_transl_deviation": 0.15, #meters
            "world_to_object_angle_deviation":30, #degrees
            "sampling": "uniform",
            "sample_only_transl_prob": 0.2,
        },
        "asset_conf":{
            "env_maps_dir": os.path.join("assets", "hdri"),
            "texture_dir": os.path.join("assets", "textures"),
            "pbr_dir": os.path.join("assets", "pbrs"),
        }
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


