import os


all_classes_modelnet40 = ["airplane", "bench", "bowl", "cone", "desk", "flower_pot", "keyboard", "mantel", "person", "radio",
                          "sofa", "table", "tv_stand", "xbox", "bathtub", "bookshelf", "car", "cup", "door", "glass_box",
                          "lamp", "monitor", "piano", "range_hood", "stairs", "tent", "vase", "bed", "bottle", "chair", "curtain",
                          "dresser", "guitar", "laptop", "night_stand", "plant", "sink", "stool", "toilet", "wardrobe"]

all_classes_modelnet10 = ["bathtub", "bed", "chair", "desk", "dresser", "monitor", "night_stand", "sofa", "table", "toilet"]


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
                "validation": 1000,
                "test": 1000,
            },

        },
        "real_render": {
            "name":"mitsuba", # pyrender or mitsuba
            "material_samplers": [
                metal_sampler("Al", -0.8, -0.3, 0.4), 
                metal_sampler("Ag", -0.8, -0.3, 0.2),
                metal_sampler("Be", -0.8, -0.3, 0.2),
                metal_sampler("Hg", -0.8, -0.3, 0.2),
                #texture_sampler("brick", 1.0)
            ],
            "samples":128,
            "path_depth":4,
            "env_map_types": ["industrial-4k"], # list or constant
            "use_spot_light_no_env":False,
            "env_map_multiplier": 1.0,
            "rgb_gamma": 2.2,
            "nested_pyrender": None,
        },
        "guess_render": pyrender_conf(True,True),
        "camera_intrinsics":{
            "focal_length": 50, #mm
            "sensor_width": 36, #mm
            "image_resolution": 720, # width=height
        },
        "scene_config":{
            "distance_cam_to_world": 2.8, #meters
            "distance_cam_to_world_deviation":0.1, #meters
            "world_to_object_gt_transl_deviation": 0.1, #meters
            "world_to_object_transl_deviation": 0.1, #meters
            "world_to_object_angle_deviation":30, #degrees
            "sampling":"normal",
            "sample_only_transl_prob":0.2,
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


