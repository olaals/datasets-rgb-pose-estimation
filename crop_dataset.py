import os
import numpy as np
import shutil
from parser_config import get_dict_from_cli
import cv2
import matplotlib.pyplot as plt
from pyrender_render import render_scene, render_normals
import yaml
from yaml.loader import SafeLoader
from se3_helpers import apply_small_random_rotation_translation
import numpy as np
import cv2
import matplotlib.pyplot as plt
#import albumentations as A



def crop_square_bounding_box(img, mask, crop_ratio):
    mask = mask.astype(np.uint8)
    img_h, img_w = img.shape[:2]
    x,y,w,h = cv2.boundingRect(mask)
    cx = x+w/2
    cy = y+h/2
    padding = max(w,h)*(crop_ratio-1)/2
    square_size = max(w,h) + padding*2
    start_x = int(max(cx - square_size/2, 0))
    start_y = int(max(cy - square_size/2, 0))
    end_x = int(min(cx+square_size/2, img_w-1))
    end_y = int(min(cy+square_size/2, img_h-1))
    w = end_x-start_x
    h = end_y-start_y
    w = min(w,h)
    h = w
    print("w", w, "h", h)
    square_crop = img[start_y:(start_y+h), start_x:(start_x+w)]
    return square_crop, (start_x, start_y, w, h)

def crop_camera_matrix(K, crop_x, crop_y):
    new_K = K
    new_K[0,2] = K[0,2] - crop_x
    new_K[1,2] = K[1,2] - crop_y
    return new_K

def copy_files(src_dir, dst_dir):
    verts_path = os.path.join(src_dir, "vertices.npy")
    shutil.copy(verts_path, dst_dir)
    metadata_path = os.path.join(src_dir, "metadata.yml")
    shutil.copy(metadata_path, dst_dir)
    T_CO_gt_path = os.path.join(src_dir, "T_CO_gt.npy")
    shutil.copy(T_CO_gt_path, dst_dir)
    #T_CO_init_path = os.path.join(src_dir, "T_CO_init.npy")
    #shutil.copy(T_CO_init_path, dst_dir)

def resize_camera_matrix(current_img_size, new_img_size, current_K):
    ratio = new_img_size*1.0/current_img_size
    new_K = current_K*ratio
    new_K[2,2] = 1.0
    return new_K

def read_yaml(yaml_path):
    with open(yaml_path) as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data

def save_rgb_cv2(img, path):
    cv2.imwrite(path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

def crop_example(src_dir, dst_dir, config):
    new_img_size = config["image_size"]
    gt_mask_path  = os.path.join(src_dir, "gt_mask.png")
    metadata_dict = read_yaml(os.path.join(src_dir, "metadata.yml"))
    T_CO_gt = np.load(os.path.join(src_dir, "T_CO_gt.npy"))
    r_range = config["r_range"]
    t_range = config["t_range"]
    T_CO_init = apply_small_random_rotation_translation(T_CO_gt, r_range, t_range)
    mesh_path = metadata_dict["unix_mesh_path"]
    mesh_path = os.path.join("3d-datasets", mesh_path)
    gt_mask = cv2.imread(gt_mask_path, cv2.IMREAD_GRAYSCALE)
    #T_CO_init = np.load(os.path.join(src_dir, "T_CO_init.npy"))
    real_img = cv2.cvtColor(cv2.imread(os.path.join(src_dir, "real.png")), cv2.COLOR_BGR2RGB)
    K = np.load(os.path.join(src_dir, "K.npy"))
    _,gt_mask = render_scene(mesh_path, T_CO_init, K=K, img_size=(gt_mask.shape[0]))
    crop_ratio_range = config["crop_ratio_range"]
    crop_ratio = np.random.uniform(crop_ratio_range[0], crop_ratio_range[1])
    real_crop, (x,y,w,h) = crop_square_bounding_box(real_img, gt_mask, crop_ratio)
    K_crop = crop_camera_matrix(K,x,y)
    real_img_rz = cv2.resize(real_crop, (new_img_size, new_img_size))
    K_crop_rz = resize_camera_matrix(w, new_img_size, K_crop)
    cv2.imwrite(os.path.join(dst_dir, "real.png"), cv2.cvtColor(real_img_rz, cv2.COLOR_RGB2BGR))
    np.save(os.path.join(dst_dir, "K.npy"), K_crop_rz)
    img_rend_gt,dep_rend_gt = render_scene(mesh_path, T_CO_gt, K=K_crop_rz, img_size=new_img_size)
    init_img,init_dep = render_scene(mesh_path, T_CO_init, K=K_crop_rz, img_size=new_img_size)
    #save_rgb_cv2((img_rend_gt*255).astype(np.uint8), os.path.join(dst_dir, "real_rend.png"))
    save_rgb_cv2((init_img*255).astype(np.uint8), os.path.join(dst_dir, "init.png"))
    np.save(os.path.join(dst_dir, "init_depth.npy"), init_dep)
    np.save(os.path.join(dst_dir, "T_CO_init.npy"), T_CO_init)
    init_normal = render_normals(mesh_path, T_CO_init, K=K_crop_rz, img_size=new_img_size)
    save_rgb_cv2((init_normal*255).astype(np.uint8), os.path.join(dst_dir, "init_normal.png"))

    




    


def crop_dataset(config):
    basedir = "img-datasets"
    crop_dataset_name = config["crop_dataset"]
    crop_dataset_path = os.path.join(basedir, crop_dataset_name)
    new_dataset_name = config["config_name"]
    new_dataset_path = os.path.join(basedir, new_dataset_name)
    crop_ds_class_paths = [os.path.join(crop_dataset_path, class_dir) for class_dir in os.listdir(crop_dataset_path) if os.path.isdir(os.path.join(crop_dataset_path, class_dir))]
    print(crop_ds_class_paths)
    for crop_ds_class_path in crop_ds_class_paths:
        ex_num = 0
        train_val_test_paths = [os.path.join(crop_ds_class_path, train_val_test_dir) for train_val_test_dir in os.listdir(crop_ds_class_path)]
        for train_val_test_path in train_val_test_paths:
            ex_dir_paths = [os.path.join(train_val_test_path, ex_dir) for ex_dir in os.listdir(train_val_test_path)]
            for ex_dir in ex_dir_paths:
                for i in range(8):
                    print(ex_dir)
                    bs = os.path.basename
                    new_ds_ex_dir = os.path.join(basedir, bs(new_dataset_name), bs(crop_ds_class_path), bs(train_val_test_path), "ex"+format(ex_num, '05d'))
                    print(new_ds_ex_dir)
                    os.makedirs(new_ds_ex_dir, exist_ok=True)
                    copy_files(ex_dir, new_ds_ex_dir)
                    crop_example(ex_dir, new_ds_ex_dir, config)
                    ex_num += 1



    


    


    pass

if __name__ == '__main__':
    config = get_dict_from_cli()
    crop_dataset(config)
