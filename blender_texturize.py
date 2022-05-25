
import sys
import pickle
import os
import subprocess
import random
import itertools


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
    new_ds = general_conf["new_texture_dataset"]
    save_filetype = bl_conf["filetype"]
    texture_ds = general_conf["texture_dataset"]
    texture_classes = class_config["texture_classes"]
    mesh_ds = general_conf["object_dataset"]
    mesh_classes = class_config["modelnet_classes"]
    n_examples_each_class = num_examples // len(mesh_classes)
    print(bl_conf)

    

    for mesh_class in mesh_classes:
        print(f'\nTexturizing {n_examples_each_class} examples from {mesh_class} in {dataset_type} set \n' )
        out_dir = os.path.join(new_ds, mesh_class, dataset_type)
        mesh_iter = itertools.cycle(get_modelnet10_class_paths(mesh_ds, mesh_class, dataset_type))
        texture_iter = itertools.cycle(get_all_texture_paths(texture_ds, texture_classes))
        os.makedirs(out_dir, exist_ok=True)
        for ex_num in range(n_examples_each_class):
            texture_path = next(texture_iter)
            mesh_path = next(mesh_iter)
            mesh_path_basename = os.path.splitext(os.path.basename(mesh_path))[0]
            tex_path_basename = os.path.splitext(os.path.basename(texture_path))[0]
            model_save_path = os.path.join(out_dir, mesh_path_basename+"-"+tex_path_basename+ "."+save_filetype)
            texturize_object(mesh_path, bl_conf, model_save_path, texture_path)

            print(texture_path)
            print(mesh_path)
            print(mesh_path_basename)
            print(model_save_path)



def get_modelnet10_class_paths(ds_path, mesh_class, train_or_test, sort_or_shuffle="sort"):
    mesh_class_dir = os.path.join(ds_path, mesh_class, train_or_test)
    all_class_meshes = [os.path.join(mesh_class_dir,filename) for filename in os.listdir(mesh_class_dir)]
    if(sort_or_shuffle == 'shuffle'):
        random.shuffle(all_class_meshes)
    elif(sort_or_shuffle == 'sort'):
        all_class_meshes.sort()
    else:
        assert False
    return all_class_meshes


def sample_modelnet10_path(ds_path, mesh_class, train_or_test):
    get_modelnet10_class_paths(ds_path, mesh_class, train_or_test)
    return random.choice(all_class_meshes)

    


def get_all_texture_paths(ds_path, texture_classes, sort_or_shuffle="shuffle"):
    all_tex_paths =  []
    for texture_class in texture_classes:
        tex_class_dir = os.path.join(ds_path, texture_class)
        all_tex_class_paths = [os.path.join(tex_class_dir,filename) for filename in os.listdir(tex_class_dir)]
        all_tex_paths = all_tex_paths + all_tex_class_paths
    
    if(sort_or_shuffle == 'shuffle'):
        random.shuffle(all_tex_paths)
    elif(sort_or_shuffle == 'sort'):
        all_tex_paths.sort()
    else:
        assert False
    return all_tex_paths


def sample_texture_path(ds_path, texture_classes):
    get_all_texture_paths(ds_path, texture_classes)
    return random.choice(all_tex_class_paths)


def texturize_object(mesh_path, blender_conf, save_path, texture_path):
    bl_exec_path = blender_conf["blender_exec_path"]
    py_path = blender_conf["py_script_path"]
    cache_dir = blender_conf["cache_dir"]
    use_draco_compression = blender_conf["use_draco_compression"]
    texturize_conf = {
            "mesh_path":mesh_path,
            "save_path":save_path,
            "texture_path":texture_path,
            "use_draco_compression": use_draco_compression,
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



