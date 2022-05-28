from parser_config import get_dict_from_cli
import os
import numpy as np
from se3_helpers import *
from mitsuba_render import sample_render_scene, sample_material, sample_metal, get_texture
from pyrender_render import render_scene, render_normals
from blender_render import bl_render_scene
import trimesh as tm
import random
import matplotlib.pyplot as plt
import cv2
import yaml

def save_img_cv2(img, path):
    cv_img = (img*254.99).astype(np.uint8)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, cv_img)

def get_vertices(mesh_path):
    mesh = tm.load(mesh_path, force='mesh')
    vertices = mesh.vertices
    return vertices

def sample_vertices(mesh_path, num_verts=1000):
    verts = get_vertices(mesh_path)
    sampled_verts = []
    for i in range(num_verts):
        vert = np.array(random.choice(verts))
        sampled_verts.append(vert)
    sampled_verts = np.array(sampled_verts, dtype=np.float32)
    return sampled_verts

def sample_mesh_path(class_dir):
    mesh_paths = [os.path.join(class_dir, filename) for filename in os.listdir(class_dir)]
    return np.random.choice(mesh_paths)

def mitsuba_handler(T_CO, obj_path, render_conf, cam_conf, train_or_test, init_or_real, save_dir, asset_paths):
    img = sample_render_scene(T_CO, obj_path, render_conf, cam_conf, train_or_test, asset_paths)
    img_save_path = os.path.join(save_dir, init_or_real+".png")
    save_img_cv2(img, img_save_path)

def pyrender_handler(T_CO, obj_path, render_conf, cam_conf, init_or_real, save_dir):
    img,depth = render_scene(obj_path, T_CO, cam_conf)
    img_save_path = os.path.join(save_dir, init_or_real+".png")
    norm_save_path = os.path.join(save_dir, init_or_real+"_normal.png")
    depth_save_path = os.path.join(save_dir, init_or_real+"_depth.npy")
    save_img_cv2(img, img_save_path)
    
    rend_normal = render_conf["render_normal"]
    rend_depth = render_conf["render_depth"]

    if rend_normal:
        normal = render_normals(obj_path, T_CO, cam_conf)
        save_img_cv2(normal, norm_save_path)

    if rend_depth:
        np.save(depth_save_path, depth)

def sample_env_map(env_map_types, env_maps_dir, train_or_test):
    env_map_class = random.choice(env_map_types)
    print(env_map_class)
    env_map_class_dir = os.path.join(env_maps_dir, env_map_class, train_or_test)
    print(env_map_class_dir)
    env_map_paths = [os.path.join(env_map_class_dir, filename) for filename in os.listdir(env_map_class_dir)]
    print(env_map_paths)
    sampled_env_map = random.choice(env_map_paths) 
    if(os.path.isdir(sampled_env_map)):
        assert False
    return sampled_env_map


def blender_handler(T_CO, obj_path, render_conf, cam_conf, train_or_test, init_or_real, save_dir, env_map_path):
    img_save_path = os.path.join(save_dir, init_or_real+".png")
    bl_render_scene(render_conf, obj_path, T_CO, cam_conf, env_map_path, 1.0, img_save_path)


def sample_texture(texture_class):
    texture_class_dir = os.path.join("assets", "textures", texture_class)
    texture_paths = [os.path.join(texture_class_dir, fn) for fn in os.listdir(texture_class_dir)]
    return random.choice(texture_paths)

def save_npy_files(ex_save_dir, mesh_path, T_CO_init, T_CO_gt, env_map_path):
    verts = sample_vertices(mesh_path, num_verts=1000)
    np.save(os.path.join(ex_save_dir, "vertices.npy"), verts)
    np.save(os.path.join(ex_save_dir, "T_CO_init.npy"), T_CO_init)
    np.save(os.path.join(ex_save_dir, "T_CO_gt.npy"), T_CO_gt)
    metadata = {}
    split = os.path.normpath(mesh_path).split(os.sep)
    metadata["mesh_filename"] = os.path.basename(mesh_path)
    metadata["train_or_test"] = split[-2]
    metadata["mesh_class"] = split[-3]
    metadata["dataset_name"] = split[-4]
    metadata["unix_mesh_path"] = os.path.join(split[-4], split[-3], split[-2], split[-1])
    if(env_map_path is not None):
        metadata["env_map_path"] = env_map_path
    metadata_save_path = os.path.join(ex_save_dir, "metadata.yml")
    with open(metadata_save_path, 'w') as outfile:
        yaml.dump(metadata, outfile, default_flow_style=False)



def process_class_dir(train_exs, dataset_type, mesh_class_dir, save_dir, config):
    gt_render_conf = config["real_render"]
    guess_render_conf = config["guess_render"]
    cam_intr = config["camera_intrinsics"]
    scene_conf = config["scene_config"]
    asset_conf = config["asset_conf"]

    os.makedirs(save_dir, exist_ok=True)
    for tr_ex in range(train_exs):
        ex_save_dir = os.path.join(save_dir, "ex"+f'{tr_ex:06d}')
        os.makedirs(ex_save_dir, exist_ok=True)
        T_CO_init, T_CO_gt = get_T_CO_init_and_gt(scene_conf)
        mesh_path = sample_mesh_path(mesh_class_dir)
        env_map_path = None
        if("env_map_types" in gt_render_conf):
            env_map_types = gt_render_conf["env_map_types"]
            env_map_path = sample_env_map(env_map_types, asset_conf["env_maps_dir"], dataset_type)
        save_npy_files(ex_save_dir, mesh_path, T_CO_init, T_CO_gt, env_map_path)

        if(gt_render_conf["name"] == "mitsuba"):
            material_sample_list = gt_render_conf["material_samplers"]
            if(material_sample_list is not None):
                gt_render_conf["material"] = sample_material(material_sample_list, asset_conf)
            else:
                gt_render_conf["material"] = None
            mitsuba_handler(T_CO_gt, mesh_path, gt_render_conf, cam_intr, dataset_type, "real", ex_save_dir, asset_conf)
        elif(gt_render_conf["name"] == "pyrender"):
            pyrender_handler(T_CO_gt, mesh_path, gt_render_conf, cam_intr, "real", ex_save_dir)
        elif(gt_render_conf["name"] == "blender"):
            blender_handler(T_CO_gt, mesh_path, gt_render_conf, cam_intr, dataset_type, "real", ex_save_dir, env_map_path)
        else:
            assert False

        if(guess_render_conf["name"] == "mitsuba"):
            guess_render_conf["material"] = gt_render_conf["material"]
            mitsuba_handler(T_CO_init, mesh_path, guess_render_conf, cam_intr, dataset_type, "init", ex_save_dir, asset_conf)
            nest_pyrender = guess_render_conf["nested_pyrender"]
            if(nest_pyrender is not None):
                pyrender_handler(T_CO_init, mesh_path, nest_pyrender, cam_intr, "init_py_ren", ex_save_dir)

        elif(guess_render_conf["name"] == "pyrender"):
            pyrender_handler(T_CO_init, mesh_path, guess_render_conf, cam_intr, "init", ex_save_dir)




def create_dataset(config):
    config_name = config["config_name"]
    img_ds_dir = os.path.join("img-datasets", config_name)
    os.makedirs(img_ds_dir, exist_ok=True)
    save_conf_path = os.path.join(img_ds_dir, "config.yml")
    with open(save_conf_path, 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


    general_conf = config["general"]


    model3d_ds_name = general_conf["dataset_name"]
    model3d_ds_path = os.path.join("3d-datasets", model3d_ds_name)
    modelnet_classes = general_conf["modelnet_classes"]
    num_classes = len(modelnet_classes)
    num_verts_sample = general_conf["num_sample_vertices"]

    train_exs = general_conf["split"]["train"]
    val_exs = general_conf["split"]["validation"]
    test_exs = general_conf["split"]["test"]
    train_exs_p_class = train_exs//num_classes
    val_exs_p_class = val_exs//num_classes
    test_exs_p_class = test_exs//num_classes

    print("Creating dataset for ModelNet classes:")
    print(modelnet_classes)
    print("Total train examples", train_exs, "with", train_exs_p_class, "examples for each class")
    print("Total validation examples", val_exs, "with", val_exs_p_class, "examples for each class")
    print("Total test examples", test_exs, "with", test_exs_p_class, "examples for each class")


    for modelnet_class in modelnet_classes:
        print("Processing", modelnet_class)
        model3d_class_dir = os.path.join(model3d_ds_path, modelnet_class, "train")

        train_class_dir = os.path.join(img_ds_dir, modelnet_class, "train")
        process_class_dir(train_exs_p_class, "train", model3d_class_dir, train_class_dir, config)

        val_class_dir = os.path.join(img_ds_dir, modelnet_class, "validation")
        process_class_dir(val_exs_p_class, "train", model3d_class_dir, val_class_dir, config)

        test_class_dir = os.path.join(img_ds_dir, modelnet_class, "test")
        process_class_dir(test_exs_p_class, "test", model3d_class_dir, test_class_dir, config)



    









if __name__ == '__main__':
    config = get_dict_from_cli()
    create_dataset(config)
