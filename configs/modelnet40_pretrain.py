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
                "train":100,
                "validation": 10,
                "test": 10,
            },

        },
        "ground_truth_render": {
            "name":"mitsuba", # pyrender or mitsuba
            "material_samplers": [
                metal_sampler("Al", -2, -0.3, 0.8), 
                metal_sampler("Ag", -2, -0.3, 0.2),
            ],
            "samples":256,
            "path_depth":4,
            "env_maps_dir": os.path.join("scene-assets", "hdri"),
            "env_map_types": ["industrial"], # list or constant
            "env_map_multiplier": 1.0,
            "rgb_gamma": 2.2,
        },
        "guess_render": {
            "name":"pyrender", # mitsuba, pyrender or none
            "render_normal":False,
        },
        "camera_intrinsics":{
            "focal_length": 50, #mm
            "sensor_width": 36, #mm
            "image_resolution": 320, # width=height
        },
        "scene_config":{
            "distance_cam_to_world": 2.0, #meters
            "distance_cam_to_world_deviation":0.1, #meters
            "world_to_object_gt_transl_deviation": 0.1, #meters
            "world_to_object_transl_deviation": 0.1, #meters
            "world_to_object_angle_deviation":30, #degrees
        },
    }


def metal_sampler(chemical_symbol, log_roughness_min, log_roughness_max, probability_weight=1.0):
    return {
        "type": "metal_sampler",
        "chemical_symbol": chemical_symbol,
        "log_roughness_min": log_roughness_min,
        "log_roughness_max": log_roughness_max,
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


