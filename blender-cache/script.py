import numpy as np
import pickle
import os
import bpy

def delete_all_entities():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def set_renderer(render_engine):
    if(render_engine == 'cycles'):
        bpy.context.scene.render.engine = 'CYCLES'

def render(write_path):
    bpy.context.view_layer.update()
    bpy.context.scene.render.filepath = write_path
    bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True, use_viewport=False, scene="scene")

def set_cycles_gpu_device():
    scene = bpy.context.scene
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.compute_device = 'CUDA_0'

def spawn_camera(T_WC):
    camera_data = bpy.data.cameras.new(name='Camera')
    camera_object = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    camera_object.matrix_world = T_WC.T
    bpy.context.scene.camera = camera_object
    print(bpy.context.scene.collection.objects[0])

def add_ply(file_path):
    bpy.ops.import_mesh.ply(filepath = file_path)

def add_hdr(hdr_path):
    C = bpy.context
    scn = C.scene

    # Get the environment node tree of the current scene
    node_tree = scn.world.node_tree
    tree_nodes = node_tree.nodes

    # Clear all nodes
    tree_nodes.clear()

    # Add Background node
    node_background = tree_nodes.new(type='ShaderNodeBackground')

    # Add Environment Texture node
    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
    # Load and assign the image to the node property
    node_environment.image = bpy.data.images.load(hdr_path) # Relative path
    node_environment.location = -300,0

    # Add Output node
    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')
    node_output.location = 200,0

    # Link all nodes
    links = node_tree.links
    link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])




delete_all_entities()


bpy.context.scene.cycles.denoiser = 'OPTIX'



bl_conf_pkl = open(os.path.join("blender-cache", "bl_conf.pkl"),'rb')
bl_conf = pickle.load(bl_conf_pkl)
bl_conf_pkl.close()

scene_config = bl_conf["scene_config"]
objects = scene_config["objects"]
for obj in objects:
    mesh_path = obj["path"]
    print(mesh_path)
    add_ply(mesh_path)
hdr = scene_config["hdr"]
hdr_path = hdr["path"]
add_hdr(hdr_path)

render_config = bl_conf["render_config"]

cam = scene_config["camera"]
cam_config = scene_config["camera"]
T_WC = cam_config["transform"]
spawn_camera(T_WC)



write_path = render_config["write_path"]


set_cycles_gpu_device()
renderer = render_config["engine"]
set_renderer(renderer)
render(write_path)



