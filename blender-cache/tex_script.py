import numpy as np
import pickle
import os
import bpy

def delete_all_entities():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def add_ply(file_path):
    bpy.ops.import_mesh.ply(filepath = file_path)



delete_all_entities()





bl_conf_pkl = open(os.path.join("blender-cache", "bl_conf_tex.pkl"),'rb')
bl_conf = pickle.load(bl_conf_pkl)
bl_conf_pkl.close()

scene_config = bl_conf["scene_config"]
mesh_path = scene_config["mesh_path"]
add_ply(mesh_path)




write_path = render_config["write_path"]





