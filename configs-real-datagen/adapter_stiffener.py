import os



def get_config():

    this_file_name = os.path.split(os.path.splitext(__file__)[0])[-1]
    print("Config file name:", this_file_name)
    return {
        "config_name":this_file_name,
        "real_dataset_path":os.path.join("real-dataset-imgs","stiffener-and-adapter"),
        "new_dataset_path":os.path.join("img-datasets","stiffener-and-adapter"),
        "camera_matrix_file":"K.npy",
        "dataset_types": ["test"],
        "image_size": 320,
    }

