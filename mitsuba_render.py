import mitsuba as mi
mi.set_variant('scalar_rgb')
from mitsuba import ScalarTransform4f
import os
import numpy as np
from se3_helpers import *
import math
import matplotlib.pyplot as plt
import spatialmath as sm
from skimage import exposure
import random


def calculate_fov_x_deg(focal_length, sensor_width):
    return 2*np.arctan((sensor_width/2)/(focal_length))*(180/math.pi)

def init_scene(path_depth=4):
    scene = {
        "type":"scene"
    }
    scene["integrator"] = {
        "type": "path",
        "max_depth":4
    }
    return scene

def add_object_ply(scene, path, material_dict):
    filename = os.path.splitext(os.path.split(path)[-1])[0]
    if(material_dict is not None):
        scene[filename] = {
            "type":"ply",
            "filename":path,
            "mat":material_dict
        }
    else:
        scene[filename] = {
            "type":"ply",
            "filename":path,
        }


def add_hdr(scene, path, scale, T_zrot):
    rot_x_90 = sm.SE3.Rx(90, unit='deg').data[0]
    scene["env_map"] = {
        "type":"envmap",
        "filename": path,
        "scale": scale,
        "to_world":ScalarTransform4f(T_zrot@rot_x_90),
    }


def calculate_fov_x_deg(focal_length, sensor_width):
    return 2*np.arctan((sensor_width/2)/(focal_length))*(180/math.pi)

def add_spot(scene, T_CO):
    assert T_CO.shape == (4,4)
    rot_z_180 = sm.SE3.Rz(180, unit='deg').data[0]
    T_WC = np.linalg.inv(T_CO)@rot_z_180 # O = W
    scene["cam_spot"] = {
        "type":"spot",
        "intensity":{
            "type":"uniform",
            "value":10.0
        },
        "cutoff_angle":80,
        "to_world": ScalarTransform4f(T_WC),
    }

def add_camera(scene, T_CO, intrinsics, sample_count):
    assert T_CO.shape == (4,4)
    rot_z_180 = sm.SE3.Rz(180, unit='deg').data[0]
    T_WC = np.linalg.inv(T_CO)@rot_z_180 # O = W
    focal_len = intrinsics["focal_length"]
    img_res = intrinsics["image_resolution"]
    sensor_width = intrinsics["sensor_width"]
    fov = calculate_fov_x_deg(focal_len, sensor_width)

    scene["camera"] = {
        "type": "perspective",
        "near_clip": 1e-3,
        "far_clip": 1000.0,
        "to_world": ScalarTransform4f(T_WC),
        "fov":fov,
        "film":{
            "type":"hdrfilm",
            "width": img_res,
            "height": img_res
        },
        "sampler":{
            "type": "independent",
            "sample_count": sample_count,
        },
    }


def render(scene, gamma=2.2):
    scene = mi.load_dict(scene)
    img = mi.render(scene)
    img = img**(1.0/gamma)
    img = np.where(img>1.0, 1.0, img)
    img = np.array(img)
    return img

    

def render_scene(obj_path, path_depth, T_CO, cam_intr, hdr_path, env_scale, material, samples, gamma):
    scene = init_scene(path_depth)
    add_camera(scene, T_CO, cam_intr, samples)
    T_zrot = get_random_z_rot().data[0]
    if(hdr_path is not None):
        add_hdr(scene, hdr_path, env_scale, T_zrot)
    else:
        add_spot(scene, T_CO)
    add_object_ply(scene, obj_path, material)
    img = render(scene, gamma)
    return img

def sample_render_scene(T_CO, obj_path, render_config, camera_config, train_or_test, asset_paths):
    assert T_CO.shape ==(4,4)
    samples = render_config["samples"]
    path_depth = render_config["path_depth"]
    gamma = render_config["rgb_gamma"]
    env_mult = render_config["env_map_multiplier"]
    env_maps_dir = asset_paths["env_maps_dir"]
    env_map_types = render_config["env_map_types"]
    use_spot_no_env = render_config["use_spot_light_no_env"]
    #mat_sample_list = render_config["material_samplers"]
    mat = render_config["material"]

    env_path = None
    if not use_spot_no_env:
        env_path = sample_env_map(env_map_types, env_maps_dir, train_or_test)

    img = render_scene(obj_path, path_depth, T_CO, camera_config, env_path, env_mult, mat, samples, gamma)
    return img.astype(np.float32)


def sample_env_map(env_map_types, env_maps_dir, train_or_test):
    env_map_type = np.random.choice(env_map_types)
    env_map_type_dir = os.path.join(env_maps_dir, env_map_type)
    env_map_type_test_train = os.path.join(env_map_type_dir, train_or_test)
    env_map_paths = [os.path.join(env_map_type_test_train, filename) for filename in os.listdir(env_map_type_test_train)]
    env_map_path = np.random.choice(env_map_paths)
    return env_map_path



def sample_material(material_sample_list, asset_paths):
    prob_list = []
    for mat_sample in material_sample_list:
        prob_list.append(mat_sample["probability_weight"])
    prob_list = np.array(prob_list)*1.0
    prob_list = prob_list/np.sum(prob_list)
    print(material_sample_list)
    sampled_material = np.random.choice(material_sample_list, 1, p=prob_list)[0]
    print("sampled mat")
    print(sampled_material)
    if(sampled_material["type"] == "metal_sampler"):
        chem_sym = sampled_material["chemical_symbol"]
        log_r_min = sampled_material["log_roughness_min"]
        log_r_max = sampled_material["log_roughness_max"]
        return sample_metal(chem_sym, log_r_min, log_r_max)
    elif(sampled_material["type"] == "texture_sampler"):
        texture_dir = asset_paths["texture_dir"]
        texture_class = sampled_material["texture_type"]
        texture_class_dir = os.path.join(texture_dir, texture_class)
        return sample_texture(texture_class_dir)
    else:
        assert False

def sample_texture(texture_class_dir):
    texture_paths = [os.path.join(texture_class_dir, fn) for fn in os.listdir(texture_class_dir)]
    return get_texture(random.choice(texture_paths))


def get_texture(texture_path):
    texture_mat = {
        "type":"diffuse",
        "reflectance":{
            "type":"bitmap",
            "filename":texture_path,
            "wrap_mode": "clamp",
        }
    }
    return texture_mat




def sample_metal(chemical_sym, log_roughness_min=-0.5, log_roughness_max=-2):
    log_sample_alpha_v = np.random.uniform(log_roughness_min, log_roughness_max)
    log_sample_alpha_u = np.random.uniform(log_roughness_min, log_roughness_max)
    alpha_v = 10**log_sample_alpha_v
    alpha_u = 10**log_sample_alpha_u
    
    metal_material = {
        "type":"roughconductor",
        "material":chemical_sym,
        "alpha_u":alpha_u,
        "alpha_v":alpha_v,
    }

    """
    material_dict = {
        "type" : "diffuse",
        "reflectance": {
            "type": "rgb",
            "value": [1.0, 1.0, 1.0]
        }
    }
    blend = {
        "type" : "blendbsdf",
        "weight":0.8,
        "mat1":alu_mat,
        "mat2":material_dict
    }
    """

    return metal_material




if __name__ == '__main__':
    """
    material_dict = {
        "type" : "diffuse",
        "reflectance": {
            "type": "rgb",
            "value": [0.05, 0.05, 0.05]
        }
    }
    """
    """
    material = sample_metal("Al")

    cam_intr = {
        "focal_length":50,
        "sensor_width":36,
        "image_resolution": 300
    }
    obj_path = "airplane_0453.ply"
    hdr_path = "industrial_pipe_and_valve_01_1k.hdr"
    T_WC = look_at_SE3([1.8,0,0], [0,0,0], [0,0,1])
    T_CO = T_WC.inv().data[0]

    img = render_scene(obj_path, 4, T_CO, cam_intr, hdr_path, 1.0, material, 128, 2.2)
    plt.imshow(img)
    plt.show()
    """

    mylist = ["hei", "hei2", "hei3"]
    probs = np.array([1, 10, 1]).astype(np.float32)
    probs = probs/np.sum(probs)
    for i in range(10):
        choose = np.random.choice(mylist, 1, p=probs)
        print(choose)






