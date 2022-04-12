from parser_config import get_dict_from_cli
import os
import numpy as np
from se3_helpers import *
from mitsuba_render import sample_render_scene
from pyrender_render import render_scene, render_normals
import trimesh as tm
import random
import matplotlib.pyplot as plt
import cv2

def save_img_cv2(img, path):
    cv_img = (img*254.01).astype(np.uint8)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, cv_img)

def get_vertices(mesh_path):
    mesh = tm.load(mesh_path)
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

def mitsuba_handler(T_CO, obj_path, render_conf, cam_conf, train_or_test, init_or_real, save_dir):
    img = sample_render_scene(T_CO, obj_path, render_conf, cam_conf, train_or_test)
    img_save_path = os.path.join(save_dir, init_or_real+".png")
    save_img_cv2(img, img_save_path)

def pyrender_handler(T_CO, obj_path, render_conf, cam_conf, train_or_test, init_or_real, save_dir):
    img,depth = render_scene(obj_path, T_CO, cam_conf)
    normal = render_normals(obj_path, T_CO, cam_conf)
    img_save_path = os.path.join(save_dir, init_or_real+".png")
    norm_save_path = os.path.join(save_dir, init_or_real+"_normal.png")
    depth_save_path = os.path.join(save_dir, init_or_real+"_depth.npy")
    save_img_cv2(img, img_save_path)
    save_img_cv2(normal, norm_save_path)
    np.save(depth_save_path, depth)

def process_class_dir(train_exs, dataset_type, mesh_class_dir, save_dir, scene_conf, cam_intr, gt_render_conf, guess_render_conf):
    os.makedirs(save_dir, exist_ok=True)
    for tr_ex in range(train_exs):
        example_save_dir = os.path.join(save_dir, "ex"+f'{tr_ex:06d}')
        os.makedirs(example_save_dir, exist_ok=True)
        T_CO_init, T_CO_gt = get_T_CO_init_and_gt(scene_conf)
        mesh_path = sample_mesh_path(mesh_class_dir)
        verts = sample_vertices(mesh_path, num_verts=1000)
        np.save(os.path.join(example_save_dir, "vertices.npy"), verts)
        np.save(os.path.join(example_save_dir, "T_CO_init.npy"), T_CO_init)
        np.save(os.path.join(example_save_dir, "T_CO_gt.npy"), T_CO_gt)
        if(gt_render_conf["name"] == "mitsuba"):
            mitsuba_handler(T_CO_gt, mesh_path, gt_render_conf, cam_intr, "train", "real", example_save_dir)
        elif(gt_render_conf["name"] == "pyrender"):
            pass
        else:
            assert False

        if(guess_render_conf["name"] == "mitsuba"):
            pass
        elif(guess_render_conf["name"] == "pyrender"):
            pyrender_handler(T_CO_init, mesh_path, guess_render_conf, cam_intr, "train", "init", example_save_dir)




def create_dataset(config):
    config_name = config["config_name"]
    img_ds_dir = os.path.join("img-datasets", config_name)
    os.makedirs(img_ds_dir, exist_ok=True)


    general_conf = config["general"]
    gt_render_conf = config["real_render"]
    guess_render_conf = config["guess_render"]
    cam_intr = config["camera_intrinsics"]
    scene_conf = config["scene_config"]


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
        process_class_dir(train_exs_p_class, "train", model3d_class_dir, train_class_dir, scene_conf, cam_intr, gt_render_conf, guess_render_conf)

        val_class_dir = os.path.join(img_ds_dir, modelnet_class, "validation")
        process_class_dir(val_exs_p_class, "train", model3d_class_dir, val_class_dir, scene_conf, cam_intr, gt_render_conf, guess_render_conf)

        test_class_dir = os.path.join(img_ds_dir, modelnet_class, "test")
        process_class_dir(test_exs_p_class, "test", model3d_class_dir, test_class_dir, scene_conf, cam_intr, gt_render_conf, guess_render_conf)



    









if __name__ == '__main__':
    config = get_dict_from_cli()
    create_dataset(config)
