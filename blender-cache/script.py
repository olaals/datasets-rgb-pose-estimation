import numpy as np
import pickle
import os
import bpy
import math
import random

def delete_all_entities():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def set_renderer(render_engine):
    if(render_engine == 'cycles'):
        bpy.context.scene.render.engine = 'CYCLES'

def set_render_settings(img_res):
    bpy.context.scene.render.resolution_y = img_res
    bpy.context.scene.render.resolution_x = img_res

def render(write_path, img_res):
    set_render_settings(img_res)
    bpy.context.view_layer.update()
    bpy.context.scene.render.filepath = write_path
    bpy.ops.render.render('INVOKE_DEFAULT', animation=False, write_still=True, use_viewport=False, scene="scene")

def set_cycles_gpu_device():
    scene = bpy.context.scene
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.compute_device = 'CUDA_0'

def spawn_camera(T_WC, camera_config):
    camera_data = bpy.data.cameras.new(name='Camera')
    camera_object = bpy.data.objects.new('Camera', camera_data)
    camera_object.data.lens = camera_config["focal_length"]
    camera_object.data.sensor_width = camera_config["sensor_width"]
    bpy.context.scene.collection.objects.link(camera_object)
    print("Actual",T_WC)
    camera_object.matrix_world = T_WC.T
    print("Cam obj",camera_object.matrix_world)
    bpy.context.scene.camera = camera_object
    bpy.context.view_layer.update()
    print(bpy.context.scene.collection.objects[0])

def add_ply(file_path):
    bpy.ops.import_mesh.ply(filepath = file_path)

def add_glb(file_path):
    print(f'\n glb file path: {file_path}\n')
    bpy.ops.import_scene.gltf(filepath=file_path)

def add_hdr(hdr_path, z_rot_deg):
    C = bpy.context
    scn = C.scene

    # Get the environment node tree of the current scene
    node_tree = scn.world.node_tree
    tree_nodes = node_tree.nodes
    # Clear all nodes
    tree_nodes.clear()

    node_map = tree_nodes.new(type='ShaderNodeMapping')
    node_map.location = -600,0
    node_map.inputs[2].default_value[2] = z_rot_deg/180*math.pi
    texture_node = tree_nodes.new(type='ShaderNodeTexCoord')
    texture_node.location=-900,0
    # Add Background node
    node_background = tree_nodes.new(type='ShaderNodeBackground')
    node_background.location = 0, 100
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
    link = links.new(node_map.outputs[0], node_environment.inputs[0])
    link = links.new(texture_node.outputs[0], node_map.inputs[0])




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
    _, mesh_filetype = os.path.splitext(mesh_path)
    if(mesh_filetype == '.ply'):
        add_ply(mesh_path)
    elif(mesh_filetype == '.glb'):
        add_glb(mesh_path)
    else:
        assert False
hdr = scene_config["hdr"]
hdr_path = hdr["path"]

z_rot_deg = random.randint(0,360)*1.0
add_hdr(hdr_path, z_rot_deg)

render_config = bl_conf["render_config"]

cam = scene_config["camera"]
cam_config = scene_config["camera"]
img_res = cam_config["image_resolution"]
T_WC = cam_config["transform"]
spawn_camera(T_WC, cam_config)


write_path = render_config["write_path"]


set_cycles_gpu_device()
renderer = render_config["engine"]
set_renderer(renderer)
render(write_path, img_res)



