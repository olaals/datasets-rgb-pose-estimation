import os
import numpy as np
import time

def pose_init_wrapper(K, img_size, img_path ,mesh_path, gt_pose_save_path):
    from kivy_gui import PoseInit, PoseInitGUI
    pose_init = PoseInit(K, img_size, img_path, mesh_path, gt_pose_save_path)
    PoseInitGUI(pose_init).run()
    PoseInitGUI(pose_init).stop()


def create_real_dataset(config):
    pass
    real_dataset_path = config["real_dataset_path"]
    new_dataset_path = config["new_dataset_path"]
    ds_classes = os.listdir(real_dataset_path)
    #ds_class_paths = [os.path.join(real_dataset_path, ds_class) for ds_class in ds_classes]
    cam_mat_file = config["camera_matrix_file"]
    dataset_types = config["dataset_types"]
    img_size = config["image_size"]
    #print(ds_class_paths)
    for ds_class in ds_classes:
        ds_class_path = os.path.join(real_dataset_path, ds_class)
        K = np.load(os.path.join(ds_class_path, cam_mat_file))
        mesh_path = os.path.join(ds_class_path, ds_class+".ply")
        for dataset_type in dataset_types:
            imgs_dir = os.path.join(ds_class_path, dataset_type)
            for idx,img_filename in enumerate(os.listdir(imgs_dir)):
                save_dir = os.path.join(new_dataset_path, ds_class, dataset_type, "ex_"+format(idx, "03d"))
                gt_pose_save_path = os.path.join(save_dir, "T_CO_gt.npy")
                os.makedirs(save_dir, exist_ok=True)
                img_path = os.path.join(imgs_dir, img_filename)
                print(K)
                print(img_size)
                print(img_path)
                print(mesh_path)
                print(gt_pose_save_path)
                pose_init_wrapper(K, img_size, img_path,mesh_path, gt_pose_save_path)
                #App.get_running_app().stop()
                time.sleep(0.1)




    







if __name__ == '__main__':
    #from parser_config import get_dict_from_cli
    #config = get_dict_from_cli()
    import sys
    sys.path.append("configs-real-datagen")
    from adapter_stiffener import get_config
    config = get_config()

    create_real_dataset(config)


    exit()


    T_CO = sm.SE3.Rx(0)

    #T_CO = sm.SE3.Tz(3).data[0]
    model3d_path = "step-files/node_adapter.ply"
    #img, d = render_scene(model3d_path, T_CO.data[0], cam_config)
    #img, d = render_scene(model3d_path, T_CO.data[0], cam_config)
    num_options = 16
