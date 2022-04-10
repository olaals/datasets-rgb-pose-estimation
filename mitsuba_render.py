import mitsuba
mitsuba.set_variant('scalar_rgb')
from mitsuba.core import Bitmap, Struct, Thread, ScalarTransform4f
from mitsuba.core.xml import load_dict
import os
import numpy as np
from se3_helpers import *
import math
import matplotlib.pyplot as plt
import spatialmath as sm

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
    scene[filename] = {
        "type":"ply",
        "filename":path,
        "mat":material_dict
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

def render(scene):
    scene = load_dict(scene)
    camera = scene.sensors()[0]
    scene.integrator().render(scene, camera)
    film = camera.film()
    bmp = film.bitmap(raw=True)
    bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
    image_np = np.array(bmp_linear_rgb)
    return image_np
    

def render_scene(object_path, T_CO, cam_intrinsics, hdr_path, material_dict):
    scene = init_scene()
    add_camera(scene, T_CO, cam_intrinsics, 256)
    T_zrot = get_random_z_rot().data[0]
    add_hdr(scene, hdr_path, 10.0, T_zrot)
    add_object_ply(scene, object_path, material_dict)
    print(scene)
    img = render(scene)
    return img




if __name__ == '__main__':
    material_dict = {
        "type" : "diffuse",
        "reflectance": {
            "type": "rgb",
            "value": [0.05, 0.05, 0.05]
        }
    }

    cam_intr = {
        "focal_length":50,
        "sensor_width":36,
        "image_resolution": 300
    }
    obj_path = "airplane_0453.ply"
    hdr_path = "industrial_pipe_and_valve_01_1k.hdr"
    T_WC = look_at_SE3([2,2,1], [0,0,0], [0,0,1])
    T_CO = T_WC.inv().data[0]

    img = render_scene(obj_path, T_CO, cam_intr, hdr_path, material_dict)
    plt.imshow(img)
    plt.show()




