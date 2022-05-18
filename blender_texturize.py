


def texturize_object(mesh_path, blender_conf, save_path, texture_path, py_path):
    texturize_conf = {
            "mesh_path":mesh_path,
    }



def call_blender_subprocess(bl_exec_path, py_path, cache_dir, texturize_conf):
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
    save_path = "blender-cache/test.png"
    blender_conf = {
        "exec_path": "/home/ola/library/blender312/blender",
        "py_script_path": "blender-cache/tex_script.py",
        "cache_dir": "blender-cache",
    }
    #call_blender_subprocess(bl_exec_path, py_path, cache_dir, texture_conf):

