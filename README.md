# Addon in Blender to export a model to Gazebo
[Русская версия](README_RU.md)
## Description

`Export model to Gazebo` is a Blender addon designed to streamline the export of models to the Gazebo format, supporting both static models and animated models. This tool automates the creation of configuration files, making it easy to prepare 3D models for simulation in Gazebo with just a few clicks.

## Key Features

- Exports models in Gazebo format with `.sdf` and `.config` files
- Supports animated models and static models
- Automatically generates waypoint-based animations using object positions and rotations from Blender
- Simple configuration options accessible through Blender’s export panel

## Installation

1. Download and unzip the repository or clone it:
    ```bash
    git clone https://github.com/VladObradovich/Export_to_Gazebo_model.git
    ```

2. Open Blender, go to `Edit > Preferences > Add-ons`, and click `Install...`.

3. Select the `addon_Gazebo.py` file from the repository folder, and click `Install Add-on`.

4. Enable the addon in the installed addons list.

## Usage

1. Go to `File > Export > Export model to Gazebo`.
2. Enter the model name for search and select the appropriate settings:

    - **Animated model** — option to export the model as an animated model.

3. Click `Export` to save `.world`, `.sdf`, and `.config` files in a folder named after the model.

## Support

If you encounter any issues, have questions, or want to request features, please use the [Issues](https://github.com/VladObradovich/Export_to_Gazebo_model/issues) section on GitHub.



---

> This addon is designed to save you time and simplify the process of preparing models for Gazebo simulations with an intuitive interface and straightforward export settings
