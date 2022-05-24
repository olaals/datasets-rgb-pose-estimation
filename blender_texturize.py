
import pickle
import os
import subprocess


def texturize_object(mesh_path, blender_conf, save_path, texture_path):
    bl_exec_path = blender_conf["exec_path"]
    py_path = blender_conf["py_script_path"]
    cache_dir = blender_conf["cache_dir"]
    texturize_conf = {
            "mesh_path":mesh_path,
            "save_path":save_path,
            "texture_path":texture_path,
    }
    call_blender_subprocess(bl_exec_path, py_path, cache_dir, texturize_conf)



def call_blender_subprocess(bl_exec_path, py_path, cache_dir, texture_conf):
    bl_pickle = open(os.path.join(cache_dir, "bl_conf_tex.pkl"), 'wb')
    pickle.dump(texture_conf, bl_pickle)
    bl_pickle.close()
    res = subprocess.run(
            [bl_exec_path, "--background", "--python", py_path])
    print("")
    print("Blender output")
    print(res)
    print("")

if __name__ == '__main__':
    obj_path = "3d-datasets/ModelNet10-norm-clean-ply/chair/train/chair_0729_opt_HR.ply"
    save_path = "blender-cache/test.gltf"
    texture_path = "/home/ola/projects/datasets-rgb-pose-estimation/texture-datasets/dtd-textures/dotted/dotted_0174.jpg"
    blender_conf = {
        "exec_path": "/home/ola/library/blender312/blender",
        "py_script_path": "blender-cache/tex_script.py",
        "cache_dir": "blender-cache",
    }
    texturize_object(obj_path, blender_conf, save_path, texture_path)
    
    #call_blender_subprocess(bl_exec_path, py_path, cache_dir, texture_conf):

