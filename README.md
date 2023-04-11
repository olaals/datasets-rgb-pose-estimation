# RGB dataset generation for pose estimation

![Alt text](docs/dataset-examples.jpg "Dataset examples")

This Github repository contains code for generating synthetic datasets for pose estimation. The pipeline uses either the Mitsuba or Blender backend to create realistic 3D models and scenes. The object under the initial pose estimate is rendered with pyrender using rasterization.

The two-step process involves generating high-quality images and then cropping them to create the final training or testing data. This approach allows researchers and developers to generate large amounts of training data and control the parameters of the scenes to create diverse scenarios for testing their pose estimation models. 

## Prerequisites
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

## Creating a dataset
```bash
python create_dataset.py configs/MN10-blender.py
```


## Cropping a dataset
```
python crop_dataset.py configs-crop
```





