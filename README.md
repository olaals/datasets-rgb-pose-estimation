# RGB dataset generation for pose estimation

![Alt text](docs/dataset-examples.jpg "Dataset examples")

This Github repository contains code for generating synthetic datasets for pose estimation. The pipeline uses either the Mitsuba or Blender backend to create realistic 3D models and scenes. The object under the initial pose estimate is rendered with pyrender using rasterization.

The two-step process involves generating high-quality images and then cropping them to create the final training or testing data. This approach allows researchers and developers to generate large amounts of training data and control the parameters of the scenes to create diverse scenarios for testing their pose estimation models. 

## Prerequisites
### Download Blender
If [Blender](https://www.blender.org/) is used as the rendering backend, download Blender and specify the path to the executable in the config file.
### 3D models
Place a 3D model dataset in 3d-datasets folder with the following structure:
```bash
3d-datasets
├── mesh_class_1
│    ├── test
│    │  ├── test_mesh_1.ply
│    │  ├── test_mesh_1.ply
│    │  └── ...
│    └── train
│       ├── train_mesh_1.ply
│       ├── train_mesh_2.ply
│       └── ...
│
└── mesh_class_2
    ├── test
    │   ├── test_mesh_1.ply
    │   ├── test_mesh_2.ply
	│   └── ...
    └── train
        ├── train_mesh_1.ply
        ├── train_mesh_2.ply
        └── ...
---
```

A 3d model dataset may have vastly different sizes of the 3D models. It is recommended to have a similar size of all 3D models such that they have similar sizes in the rendering (see [normalization script](3d-datasets/normalize_modelnet10_cleaned.py)). An example of a 3D model dataset found online is [Modelnet10/40](https://modelnet.cs.princeton.edu/).



### Textures
Object materials can either be generated procedurally or with download textures.
For downloaded textures, place it in [assets/pbrs](assets/pbrs) such as [Metal001_1K-JPG](assets/pbrs/metal/Metal001_1K-JPG)
More materials can be found at [ambientcg](https://ambientcg.com/)

### Background
Backgrounds granting realstic lightning is included in the form of HDR images. The HDR images are placed in [assets/hdri](assets/hdri). More HDRIs can be found at [polyhaven](https://polyhaven.com/hdris)



## Creating a dataset
The creation of a dataset is split into two parts, rendering and cropping. Rendering is a time consuming process, and specifying the exact parameters of the intial pose estimates and crop may save time if redone.
### Rendering
To create a rendered dataset run the following command
```bash
python create_dataset.py configs/MN10-blender.py
```

### Cropping a dataset
To create the final cropped dataset with initial pose estimates run the following command
```
python crop_dataset.py configs-crop
```





