import os


all_classes_modelnet10 = ["bathtub", "bed", "chair", "desk", "dresser", "monitor", "night_stand", "sofa", "table", "toilet"]


def get_config():

    this_file_name = os.path.split(os.path.splitext(__file__)[0])[-1]
    print("Config file name:", this_file_name)




    return {
        "config_name":this_file_name,
        "general":{
            "modelnet_classes": all_classes_modelnet10, # all_classes or specify indivudal as ["desk", "sofa", "plant"]
            "num_sample_vertices": 1000,  # number of vertices sampled from the mesh
            "dataset_name": "ModelNet10-texturized",
            #"dataset_name": "ModelNet10-norm-clean-ply",
            "split":{
                "train":30000,
                "validation": 160,
                "test": 1000,
            },

        },
        "real_render": {
            "name":"blender", # pyrender or mitsuba
            "env_map_types": ["industrial", "indoor", "outdoor-day"], # list or constant
            "exec_path":"/home/ola/library/blender312/blender",
            "py_script_path":"blender-cache/script.py",
            "cache_dir":"blender-cache",
            "nested_pyrender": None,
        },
        "guess_render": pyrender_conf(True,True),
        "camera_intrinsics":{
            "focal_length": 50, #mm
            "sensor_width": 36, #mm
            "image_resolution": 320, # width=height
        },
        "scene_config":{
            "distance_cam_to_world": 2.5, #meters
            "distance_cam_to_world_deviation":0.1, #meters
            "world_to_object_gt_transl_deviation": 0.1, #meters
            "world_to_object_transl_deviation": 0.1, #meters
            "world_to_object_angle_deviation":30, #degrees
        },
        "asset_conf":{
            "env_maps_dir": os.path.join("assets", "hdri"),
            "texture_dir": os.path.join("assets", "textures"),
        }
    }

def pyrender_conf(render_normal=False, render_depth=False):
    return {
        "name":"pyrender",
        "render_normal":render_normal,
        "render_depth":render_depth,
    }


def metal_sampler(chemical_symbol, log_roughness_min, log_roughness_max, probability_weight=1.0):
    return {
        "type": "metal_sampler",
        "chemical_symbol": chemical_symbol,
        "log_roughness_min": log_roughness_min,
        "log_roughness_max": log_roughness_max,
        "probability_weight": probability_weight,
    }

def texture_sampler(texture_type, probability_weight=1.0):
    return {
        "type": "texture_sampler",
        "texture_type": texture_type,
        "probability_weight": probability_weight,
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


