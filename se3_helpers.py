import spatialmath as sm
import random
import numpy as np


def look_at_SE3(origin, target, up):
    """
    Useful for positioning the camera in a scene. 
    Origin: The position of the camera, for example [3,3,3] means that the x,y,z location of the camera is at x=3, y=3, z=3
    Target: The point in space the camera 'looks' at
    Up: The direction in world coordinates that defines which "roll" the camera has. Usually [0,0,1]
    """
    assert len(origin) == 3
    assert len(target) == 3
    assert len(up) == 3
    origin= np.array(origin)
    target = np.array(target)
    up = np.array(up)
    z = target - origin
    z = z/np.linalg.norm(z)
    x = np.cross(up, z)
    x = -x/np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.array([x,y,z]).transpose()
    so3_sm = sm.SO3(R, check=True)
    se3_sm = sm.SE3.Rt(so3_sm, origin)
    return se3_sm

def get_random_z_rot():
    z_rot = np.random.uniform(-180.0, 180.0)
    T_zrot = sm.SE3.Rz(z_rot, unit='deg')
    return T_zrot


def get_random_unit_axis(dim=3):
    # not perfectly random, as points are sampled uniformly in a cube then normalized to unit length
    random_axis = np.random.random(dim)-0.5
    random_unit_axis = random_axis/np.linalg.norm(random_axis)
    return random_unit_axis



"""
def apply_small_random_rotation_translation(T, theta_range_deg, xyz_transl_range, sample_on_transl_prob=0.0, sampling='uniform'):
    if sampling == "uniform":
        if np.random.random() > sample_on_transl_prob:
            theta = np.random.uniform(theta_range_deg[0], theta_range_deg[1])*random.choice((-1, 1))
        else:
            theta = 0.0
        print("Theta: ", theta)
        transl_len = np.random.uniform(xyz_transl_range[0], xyz_transl_range[1])
        transl = get_random_unit_axis()*transl_len
    rotation_axis = get_random_unit_axis()
    rotation_SO3 = sm.SO3.AngleAxis(theta,rotation_axis, unit='deg')
    delta_SE3 = sm.SE3.Rt(rotation_SO3, transl)
    new_SE3 = T*delta_SE3
    return new_SE3
"""


def apply_small_random_rotation_translation(T, theta_range_deg, xyz_transl_range):
    theta = np.random.uniform(theta_range_deg[0], theta_range_deg[1])*random.choice((-1, 1))
    print("Theta: ", theta)
    unit_vec = get_random_unit_axis(3)
    transl_len = np.random.uniform(xyz_transl_range[0], xyz_transl_range[1])
    transl = unit_vec*transl_len
    print("transl", transl)

    rotation_axis = get_random_unit_axis()
    rotation_SO3 = sm.SO3.AngleAxis(theta,rotation_axis, unit='deg')
    delta_SE3 = sm.SE3.Rt(rotation_SO3, transl)
    print(delta_SE3)
    new_SE3 = T@delta_SE3.data[0]
    print(type(new_SE3))
    new_SE3 = new_SE3.astype(np.float32)
    return new_SE3


def get_random_rotation_translation(xyz_transl_range):
    theta = np.random.uniform(0, 360)
    rotation_axis = get_random_unit_axis()
    rotation_SO3 = sm.SO3.AngleAxis(theta,rotation_axis, unit='deg')
    x_transl = np.random.normal(0, xyz_transl_range)
    y_transl = np.random.normal(0, xyz_transl_range)
    z_transl = np.random.normal(0, xyz_transl_range)
    transl = np.array([x_transl, y_transl, z_transl])
    SE3_mat = sm.SE3.Rt(rotation_SO3, transl)
    return SE3_mat

def get_T_CW(base_distance, random_deviation=0.0):
    distance = base_distance + np.random.uniform(-random_deviation, random_deviation)
    T_WC = look_at_SE3([distance, 0, 0], [0,0,0], [0,0,1])
    T_CW = T_WC.inv()
    return T_CW

def get_T_CO_gt(scene_config):
    dist_CW = scene_config["distance_cam_to_world"]
    dist_CW_dev = scene_config["distance_cam_to_world_deviation"]
    WO_gt_transl_dev = scene_config["world_to_object_gt_transl_deviation"]
    WO_transl_dev = scene_config["world_to_object_transl_deviation"]
    WO_angle_dev = scene_config["world_to_object_angle_deviation"]
    if "sampling" in scene_config:
        pose_sampling = scene_config["sampling"]
    else:
        pose_sampling='uniform'
    sample_only_transl_prob = scene_config["sample_only_transl_prob"]
     
    T_WO_gt = get_random_rotation_translation(WO_gt_transl_dev)
    T_CW = get_T_CW(dist_CW, dist_CW_dev)
    T_CO_gt = T_CW*T_WO_gt
    return T_CO_gt


def get_T_CO_init_and_gt(scene_config, sampling='uniform'):
    dist_CW = scene_config["distance_cam_to_world"]
    dist_CW_dev = scene_config["distance_cam_to_world_deviation"]
    WO_gt_transl_dev = scene_config["world_to_object_gt_transl_deviation"]
    WO_transl_dev = scene_config["world_to_object_transl_deviation"]
    WO_angle_dev = scene_config["world_to_object_angle_deviation"]
    if "sampling" in scene_config:
        pose_sampling = scene_config["sampling"]
    else:
        pose_sampling='uniform'
    sample_only_transl_prob = scene_config["sample_only_transl_prob"]
     
    T_WO_gt = get_random_rotation_translation(WO_gt_transl_dev)
    T_WO_init_guess = apply_small_random_rotation_translation(T_WO_gt, WO_angle_dev, WO_transl_dev)
    T_CW = get_T_CW(dist_CW, dist_CW_dev)
    T_CO_gt = T_CW*T_WO_gt
    T_CO_init_guess = T_CW*T_WO_init_guess
    T_CO_init = T_CO_init_guess.data[0].astype(np.float32)
    T_CO_gt = T_CO_gt.data[0].astype(np.float32)
    return T_CO_init, T_CO_gt


def get_T_CO_init_given_gt(T_CO_gt, WO_angle_dev, WO_transl_dev):
    print(T_CO_gt)
    T_WO_gt = sm.SE3.Rx(0)
    print("T_WO_gt")
    print(T_WO_gt)
    T_CW = T_CO_gt*sm.SE3(T_WO_gt).inv()
    print("T_CW")
    print(T_CW)
    T_WO_init_guess = apply_small_random_rotation_translation(T_WO_gt, WO_angle_dev, WO_transl_dev)
    print("T_WO_init_guess")
    print(T_WO_init_guess)
    T_CO_init_guess = T_CW*T_WO_init_guess
    #print("T_CO_init_guess")
    #print(T_CO_init_guess)
    return T_CO_init_guess.data[0]

    




if __name__ == '__main__':
    scene_config={
        "distance_cam_to_world": 2.5, #meters
        "distance_cam_to_world_deviation":0.1, #meters
        "world_to_object_gt_transl_deviation": 0.1, #meters
        "world_to_object_transl_deviation": 0.1, #meters
        "world_to_object_angle_deviation":30, #degrees
    }

    T_CO_init, T_CO_gt = get_T_CO_init_and_gt(scene_config)
    print(T_CO_init)
    print(T_CO_gt)




