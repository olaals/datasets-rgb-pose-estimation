import numpy as np
import pickle
import os
import bpy
from bpy import context, data, ops

def delete_all_entities():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def add_ply(file_path):
    bpy.ops.import_mesh.ply(filepath = file_path)


def texturize_object(mesh_path, blender_conf, save_path, texture_path):
    bl_exec_path = blender_conf["exec_path"]
    py_path = blender_conf["py_script_path"]
    cache_dir = blender_conf["cache_dir"]
    texturize_conf = {
            "mesh_path":mesh_path,
            "save_path":save_path,
            "texture_path":texture_path,
    }
    return texturize_conf

def texturize(bl_conf):
    print(bl_conf)
    mesh_path = bl_conf["mesh_path"]
    texture_path = bl_conf["texture_path"]
    save_path = bl_conf["save_path"]
    use_draco_compression = bl_conf["use_draco_compression"]
    add_ply(mesh_path)
    smart_project_uv()
    ob = bpy.context.active_object
    texture_mat(ob, texture_path)
    bpy.ops.export_scene.gltf(
        filepath=save_path,
        use_selection=True,
        export_draco_mesh_compression_enable=use_draco_compression,
        export_yup=False,
    )


def smart_project_uv():
    bpy.ops.object.editmode_toggle()
    bpy.ops.uv.smart_project()
    bpy.ops.object.editmode_toggle()



def texture_mat(ob, texture_path):
    mat = bpy.data.materials.new(name="New_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(texture_path)
    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

    # Assign it to object
    if ob.data.materials:
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)


if __name__ == '__main__':
    bl_conf_pkl = open(os.path.join("blender-cache", "bl_conf_tex.pkl"),'rb')
    bl_conf = pickle.load(bl_conf_pkl)
    bl_conf_pkl.close()
    texturize(bl_conf)










