import os


def get_config():
    this_file_name = os.path.split(os.path.splitext(__file__)[0])[-1]
    print("Config file name:", this_file_name)
    return {
        "config_name":this_file_name,
        "crop_dataset":"MN10-blender",
        "crop_ratio_range": (1.4,1.4),
        "image_size":320,
        "center_offset":10,
        "r_range":(0.0,30),
        "t_range":(0.0,0.5),
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


