import trimesh as tm
import numpy as np
#import pymeshfix
import os



def center_mesh_to_centroid(mesh):
    c = mesh.centroid
    transf = np.eye(4)
    transf[:3, 3] = -c
    mesh.apply_transform(transf)

def rescale_mesh(mesh):
    bounding_box = mesh.extents
    longest_axis = np.max(bounding_box)
    transf_mat = np.eye(4)
    transf_mat[:3,:3] = transf_mat[:3, :3]/longest_axis
    mesh.apply_transform(transf_mat)

def decimate_mesh(mesh, ratio):
    current_faces = len(mesh.faces)
    new_faces = int(current_faces*ratio)
    simplified = mesh.simplify_quadratic_decimation(new_faces)
    return simplified

def repair_mesh(mesh):
    tm.repair.fix_normals(mesh)
    tm.repair.fix_winding(mesh)
    tm.repair.fill_holes(mesh)
    tm.repair.fix_inversion(mesh)

def fix_mesh(mesh):
    vclean, fclean = pymeshfix.clean_from_arrays(mesh.vertices, mesh.faces)
    return tm.Trimesh(vclean, fclean)


def change_extension(filename, new_extension):
    without_ext = os.path.splitext(filename)[0]
    with_new_ext = without_ext+"."+new_extension
    return with_new_ext



"""
Download the cleaned ModelNet10 from https://github.com/lei65537/Visual_Driven_Mesh_Repair
Change ABS_PATH_TO_MODELNET40 depending on where it is located on you pc.
If the assert statement fails, fix the absolute path
"""

ABS_PATH_TO_MODELNET40 = "/home/ola/library/datasets/ModelNet10-clean" 
OUTPUT_FILE_FORMAT = "ply"
OUTPUT_DATASET_DIR = "ModelNet10-norm-clean-"+OUTPUT_FILE_FORMAT
FILE_END_FILTER = "opt_HR.obj"

ds_path = ABS_PATH_TO_MODELNET40
classes = os.listdir(ds_path)
assert "chair" in classes and "bed" in classes and "night_stand" in classes

os.makedirs(OUTPUT_DATASET_DIR, exist_ok=True)
train_type = ["test", "train"]
for classname in classes:
    for train_or_test in train_type:
        print("Processing", classname, "in", train_or_test)
        read_dir = os.path.join(ds_path, classname, train_or_test)
        read_files = [os.path.join(read_dir, filename) for filename in os.listdir(read_dir)]
        out_dir = os.path.join(OUTPUT_DATASET_DIR, classname, train_or_test)
        os.makedirs(out_dir, exist_ok=True)
        out_files = [os.path.join(out_dir, change_extension(filename, OUTPUT_FILE_FORMAT)) for filename in os.listdir(read_dir)]
        for (read_file, out_file) in zip(read_files, out_files):
            if read_file.endswith(FILE_END_FILTER):
                mesh = tm.load(read_file, force='mesh', skip_texture=True)
                rescale_mesh(mesh)
                center_mesh_to_centroid(mesh)
                #mesh.show()
                #mesh = fix_mesh(mesh)
                result = tm.exchange.ply.export_ply(mesh)
                output_file = open(out_file, "wb+")
                output_file.write(result)
                output_file.close()













