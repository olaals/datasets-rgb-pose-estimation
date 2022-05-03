import numpy as np
import pickle
import os
import subprocess
from se3_helpers import look_at_SE3
import spatialmath as sm
import matplotlib.pyplot as plt

def add_camera(scene, intrinsics, T_WC):
    assert T_WC.shape == (4,4)
    #rot_z_180 = sm.SE3.Rz(180, unit='deg').data[0]
    rot_x_180 = sm.SE3.Rx(180, unit='deg').data[0]
    T_WC = T_WC@rot_x_180
    T_WC_sm = sm.SE3(T_WC)
    T_WC_sm.plot()
    plt.show()
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

def cycles_render_conf(device, write_path):
    assert (device == 'gpu' or device == 'cpu')
    return {
        "engine":"cycles",
        "device": device,
        "write_path": write_path,
    }

def bl_render_scene(blender_conf, obj_path, T_CO, cam_intr, hdr_path, env_intsy, save_path):
    scene = init_scene()
    add_object(scene, obj_path, np.identity(4))
    T_WC = T_CO.inv().data[0]
    add_camera(scene, cam_intr, T_WC)
    render_conf = cycles_render_conf("gpu", save_path)
    add_hdr(scene, hdr_path, env_intsy, 0.0)
    bl_exec_path = blender_conf["exec_path"]
    py_script_path = blender_conf["py_script_path"]
    cache_dir = blender_conf["cache_dir"]

    call_blender_subprocess(bl_exec_path, py_script_path, cache_dir, scene, render_conf)





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


if __name__ == '__main__':
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





