
import sys
import pickle
import os
import subprocess
import random

def create_dataset(config):
    
    bl_conf = config["blender_config"]
    train_conf = config["train_config"]
    test_conf = config["test_config"]
    dataset_split = config["dataset_split"]
    general_conf = config["general"]

    train_examples = dataset_split["train"]
    test_examples = dataset_split["test"]

    create_subset("train", train_examples, train_conf, bl_conf, general_conf)
    create_subset("test", test_examples, train_conf, bl_conf, general_conf)


def create_subset(dataset_type, num_examples, class_config, bl_conf, general_conf):
    texture_ds = general_conf["texture_dataset"]
    texture_classes = class_config["texture_classes"]
    for ex_num in range(num_examples):
        texture_path = sample_texture_path(texture_ds, texture_classes)
        print(texture_path)





def sample_texture_path(ds_path, texture_classes):
    sampled_class = random.choice(texture_classes)
    tex_class_dir = os.path.join(ds_path, sampled_class)
    all_tex_class_paths = [os.path.join(tex_class_dir,filename) for filename in os.listdir(tex_class_dir)]
    return random.choice(all_tex_class_paths)


def texturize_object(mesh_path, blender_conf, save_path, texture_path):
    bl_exec_path = blender_conf["exec_path"]
    py_path = blender_conf["py_script_path"]
    cache_dir = blender_conf["cache_dir"]
    texturize_conf = {
            "mesh_path":mesh_path,
            "save_path":save_path,
            "texture_path":texture_path,
    }
    call_blender_subprocess(bl_exec_path, py_path, cache_dir, texturize_conf)



def call_blender_subprocess(bl_exec_path, py_path, cache_dir, texture_conf):
    bl_pickle = open(os.path.join(cache_dir, "bl_conf_tex.pkl"), 'wb')
    pickle.dump(texture_conf, bl_pickle)
    bl_pickle.close()
    res = subprocess.run(
            [bl_exec_path, "--background", "--python", py_path])
    print("")
    print("Blender output")
    print(res)
    print("")

if __name__ == '__main__':
    sys.path.append("configs-texturize")
    from texturize import get_config
    config = get_config()
    create_dataset(config)
    """
    obj_path = "3d-datasets/ModelNet10-norm-clean-ply/chair/train/chair_0729_opt_HR.ply"
    save_path = "blender-cache/test.gltf"
    texture_path = "/home/ola/projects/datasets-rgb-pose-estimation/texture-datasets/dtd-textures/dotted/dotted_0174.jpg"
    blender_conf = {
        "exec_path": "/home/ola/library/blender312/blender",
        "py_script_path": "blender-cache/tex_script.py",
        "cache_dir": "blender-cache",
        "use_draco_compression":False,
    }
    texturize_object(obj_path, blender_conf, save_path, texture_path)
    """
    
    #call_blender_subprocess(bl_exec_path, py_path, cache_dir, texture_conf):



