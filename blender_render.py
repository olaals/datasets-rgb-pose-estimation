import numpy as np
import pickle
import os
import subprocess
from se3_helpers import look_at_SE3
import spatialmath as sm
import matplotlib.pyplot as plt
from spatialmath.base import trnorm

def plot_SE3(T):
    T = trnorm(T)
    R = sm.SO3(trnorm(T[:3,:3]))
    T = sm.SE3.Rt(R, T[:3,3])
    print("T_WC")
    print(T.data[0])
    T_orig = sm.SE3.Rx(0)
    T_orig.plot(color='red')
    T.plot( dims=[-3, 3, -3, 3, -3, 3])
    plt.show()


def add_camera(scene, intrinsics, T_CO):
    #rot_z_180 = sm.SE3.Rz(180, unit='deg').data[0]
    T_CO = sm.SE3.Rx(180, unit='deg').data[0]@T_CO
    T_WC = np.linalg.inv(T_CO)
    #plot_SE3(T_WC)
    print("T_WC blender", T_WC)

    scene["camera"] = intrinsics
    scene["camera"]["transform"] = T_WC

def add_hdr(scene, hdr_path, intensity, rotation):
    scene["hdr"] = {
        "path":hdr_path,
        "intensity":intensity,
        "rotation":rotation,
    }

def init_scene():
    scene = {
        "objects":[],
        "hdr":None,
        "camera":None
    }
    return scene

def add_object(scene, mesh_path, T_WO):
    print(scene)
    scene["objects"].append({
        "path":mesh_path,
        "transform":T_WO
    })

def add_material(scene, material_dict):
    scene["material"] = material_dict

def cycles_render_conf(device, write_path):
    assert (device == 'gpu' or device == 'cpu')
    return {
        "engine":"cycles",
        "device": device,
        "write_path": write_path,
    }



def bl_render_scene(blender_conf, obj_path, T_CO, cam_intr, hdr_path, env_intsy, save_path, asset_conf):
    scene = init_scene()
    add_object(scene, obj_path, np.identity(4))
    add_camera(scene, cam_intr, T_CO)
    render_conf = cycles_render_conf("gpu", save_path)
    add_hdr(scene, hdr_path, env_intsy, 0.0)
    bl_exec_path = blender_conf["exec_path"]
    py_script_path = blender_conf["py_script_path"]
    cache_dir = blender_conf["cache_dir"]
    # assign material
    material_sample_list = blender_conf["material_samplers"]
    material = sample_material(material_sample_list, asset_conf)
    add_material(scene, material)
    call_blender_subprocess(bl_exec_path, py_script_path, cache_dir, scene, render_conf)


def sample_material(material_sample_list, asset_paths):
    prob_list = []
    for mat_sample in material_sample_list:
        prob_list.append(mat_sample["probability_weight"])
    prob_list = np.array(prob_list)*1.0
    prob_list = prob_list/np.sum(prob_list)
    print(material_sample_list)
    sampled_material = np.random.choice(material_sample_list, 1, p=prob_list)[0]
    if sampled_material["type"] == 'pbr':
        return sample_pbr(sampled_material, asset_paths)
    elif sampled_material["type"] == 'bsdf-metal':
        return sample_bsdf_metal(sampled_material, asset_paths)
    elif sampled_material["type"] == 'standard':
        return sampled_material
    else:
        print("Material type is not implemented")
        assert False

def sample_pbr(pbr_dict, asset_conf):
    print("sample pbr")
    print(pbr_dict)
    pbr_type = pbr_dict["pbr_type"]
    pbr_dir = asset_conf["pbr_dir"]
    roughness_range = pbr_dict["roughness_range"]
    roughness = np.random.uniform(roughness_range[0], roughness_range[1])
    pbr_dir_path = os.path.join(pbr_dir, pbr_type)
    pbr_paths_list = [os.path.join(pbr_dir_path, dirname) for dirname in os.listdir(pbr_dir_path)]
    sampled_pbr_path = np.random.choice(pbr_paths_list)
    pbr_dict = {
        "type": "pbr",
        "dir_path": sampled_pbr_path,
        "roughness": roughness
    }
    print("pbr dict")
    print(pbr_dict)
    return pbr_dict

def sample_bsdf_metal(bsdf_metal_dict, asset_conf):
    print("sample bsdf metal")
    roughness_range = bsdf_metal_dict["roughness_range"]
    base_color_range = bsdf_metal_dict["base_color_range"]
    roughness = np.random.uniform(roughness_range[0], roughness_range[1])
    base_color = np.random.uniform(base_color_range[0], base_color_range[1])

    bsdf_metal_dict = {
            "type": "bsdf-metal",
            "roughness": roughness,
            "base_color": base_color,
    }
    return bsdf_metal_dict





def call_blender_subprocess(bl_exec_path, py_path, cache_dir, scene_conf, render_conf):
    bl_config = {
        "scene_config":scene_conf,
        "render_config":render_conf
    }
    bl_pickle = open(os.path.join(cache_dir, "bl_conf.pkl"), 'wb')
    pickle.dump(bl_config, bl_pickle)
    bl_pickle.close()
    res = subprocess.run(
            [bl_exec_path, "--background", "--python", py_path])
    print("")
    print("Blender output")
    print(res)
    print("")

def test_render():
    obj_path = "3d-datasets/ModelNet10-norm-clean-ply/chair/train/chair_0729_opt_HR.ply"
    T_WC = look_at_SE3([5,5,1],[0,0,0],[0,0,1])
    T_WC.plot()
    plt.show()
    print(T_WC)
    T_CO = T_WC.inv()
    cam_intr = {
        "focal_length": 50,
        "sensor_width": 36, 
        "image_resolution": 320, 
    }
    hdr_path = "assets/hdri/industrial/train/small_hangar_01_1k.hdr"
    save_path = "blender-cache/test.png"
    blender_conf = {
        "exec_path": "/home/ola/library/blender312/blender",
        "py_script_path": "blender-cache/script.py",
        "cache_dir": "blender-cache",
    }
    bl_render_scene(blender_conf, obj_path, T_CO, cam_intr, hdr_path, 1.0, save_path)


if __name__ == '__main__':
    mat1 = {
        ""
    }



