import os
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, BoolProperty

bl_info = {
    'name': "Export model to Gazebo",
    'blender': (3, 0, 0),
    'category': "Import-Export",
    'author': "Vlad Obradovich",
    'version': (1, 0, 0),
    'location': "File > Export > Export model to Gazebo",
    'description': "Export model to Gazebo",
    'tracker_url': "https://github.com/VladObradovich/Export_to_Gazebo_model/issues",
    'doc_url': "https://github.com/VladObradovich/Export_to_Gazebo_model/blob/main/README.md",
    'warning': ""}


def delete_png_files_in_meshes_folder(meshes_folder):
    if not os.path.exists(meshes_folder):
        return

    for file_name in os.listdir(meshes_folder):
        file_path = os.path.join(meshes_folder, file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith('.png'):
            os.remove(file_path)
            print(f"Удален файл: {file_path}")

class ExportAnimation(Operator, ExportHelper):
    bl_idname = "export.animation"
    bl_label = "Export model to Gazebo"
    filename_ext = '.world'
    filter_glob: StringProperty(default="*.world", options={'HIDDEN'})

    search_name: StringProperty(name="Model Name")
    fps: IntProperty(name="FPS", default=10, min=1)
    is_static: BoolProperty(name="Animated model", default=False)

    def execute(self, context):
        scene = context.scene
        objects = bpy.data.objects
        matched_objects = [obj for obj in objects if self.search_name.lower() in obj.name.lower()]

        if not matched_objects:
            self.report({'ERROR'}, "No objects found with the given name")
            return {'CANCELLED'}

        for obj in matched_objects:
            model_name = obj.name

            export_folder = os.path.join(os.path.dirname(self.filepath), model_name)
            os.makedirs(export_folder, exist_ok=True)

            meshes_folder = os.path.join(export_folder, "meshes")
            os.makedirs(meshes_folder, exist_ok=True)

            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
            dae_path = os.path.join(meshes_folder, f"{model_name}.dae")
            stl_path = os.path.join(meshes_folder, f"{model_name}.stl")

            bpy.ops.wm.collada_export(filepath=dae_path)
            bpy.ops.export_mesh.stl(filepath=stl_path)
            delete_png_files_in_meshes_folder(meshes_folder)
            obj.select_set(False)

            config_content = f"""<?xml version="1.0" ?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf>model.sdf</sdf>
  <author>
    <name>Vlad Obradovich</name>
    <email>vladislav.icgod@gmail.com</email>
  </author>
  <description>Model description here.</description>
</model>
"""
            config_path = os.path.join(export_folder, "model.config")
            with open(config_path, 'w') as config_file:
                config_file.write(config_content)

            sdf_content = f"""<sdf version="1.6">
  <model name="{model_name}">
    <static>{'true' if self.is_static else 'false'}</static>
    <link name="link">
      <pose>0 0 0 0 0 0</pose>
      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{model_name}.dae</uri>
            <scale>1 1 1</scale>
          </mesh>
        </geometry>
      </visual>
      <collision name="collision">
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{model_name}.stl</uri>
            <scale>1 1 1</scale>
          </mesh>
        </geometry>
      </collision>
    </link>
  </model>
</sdf>
"""
            sdf_path = os.path.join(export_folder, "model.sdf")
            with open(sdf_path, 'w') as sdf_file:
                sdf_file.write(sdf_content)

            world_file_path = os.path.join(export_folder, f"{model_name}.world")

            world_start_content = f"""<sdf version="1.5">
  <world name="default">
    
    <include>
      <uri>model://sun</uri>
    </include>
    <include>
      <uri>model://parquet_plane</uri>
      <pose>0 0 -0.01 0 0 0</pose>
    </include>

    <scene>
      <ambient>0.8 0.8 0.8 1</ambient>
      <background>0.8 0.9 1 1</background>
      <shadows>false</shadows>
      <grid>false</grid>
      <origin_visual>false</origin_visual>
    </scene>
"""

            if self.is_static:
                model_content = f"""    <actor name="{model_name}">
      <link name="link">
        <visual name="visual">
          <geometry>
            <mesh>
              <scale>1 1 1</scale>
              <uri>model://{model_name}/meshes/{model_name}.dae</uri>
            </mesh>
          </geometry>
        </visual>
      </link>
      <script>
        <loop>true</loop>
        <delay_start>0.000000</delay_start>
        <auto_start>true</auto_start>
        <trajectory id="0" type="square">
"""

                action = obj.animation_data.action if obj.animation_data else None
                if action:
                    frame_start = int(action.frame_range[0])
                    frame_end = int(action.frame_range[1])

                    for frame in range(frame_start, frame_end + 1):
                        scene.frame_set(frame)
                        time = frame / self.fps

                        loc = obj.location
                        rot = obj.rotation_euler

                        pose = f"{loc.x:.7f} {loc.y:.7f} {loc.z:.7f} {rot.x:.7f} {rot.y:.7f} {rot.z:.7f}"
                        model_content += f"""          <waypoint>
            <time>{time:.1f}</time>
            <pose>{pose}</pose>
          </waypoint>
"""
                model_content += """        </trajectory>
      </script>
    </actor>
"""
            else:
                model_content = f"""    <model name='{model_name}'>
      <link name='link'>
        <self_collide>0</self_collide>
        <enable_wind>0</enable_wind>
        <kinematic>0</kinematic>
        <pose>0 0 0 0 -0 0</pose>
        <gravity>1</gravity>
        <inertial>
          <mass>1</mass>
          <pose>0 0 0 0 -0 0</pose>
          <inertia>
            <ixx>1</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>1</iyy>
            <iyz>0</iyz>
            <izz>1</izz>
          </inertia>
        </inertial>
        <visual name='visual'>
          <geometry>
            <mesh>
              <scale>1 1 1</scale>
              <uri>model://{model_name}/meshes/{model_name}.dae</uri>
            </mesh>
          </geometry>
          <material>
            <shader type='pixel'>
              <normal_map>__default__</normal_map>
            </shader>
            <script>
              <name>ModelPreview_1::link::visual_MATERIAL_</name>
              <uri>__default__</uri>
            </script>
            <diffuse>0.976 0.941 0.42 1</diffuse>
            <ambient>0.976 0.941 0.42 1</ambient>
            <specular>0 0 0 1</specular>
            <emissive>0 0 0 1</emissive>
          </material>
          <pose>0 0 0 0 -0 0</pose>
          <transparency>0</transparency>
          <cast_shadows>1</cast_shadows>
        </visual>
        <collision name='collision'>
          <laser_retro>0</laser_retro>
          <max_contacts>10</max_contacts>
          <pose>0 0 0 0 -0 0</pose>
          <geometry>
            <mesh>
              <uri>model://{model_name}/meshes/{model_name}.stl</uri>
              <scale>1 1 1</scale>
            </mesh>
          </geometry>
          <surface>
            <friction>
              <ode/>
              <torsional>
                <ode/>
              </torsional>
            </friction>
            <bounce/>
            <contact>
              <collide_without_contact>0</collide_without_contact>
              <collide_without_contact_bitmask>1</collide_without_contact_bitmask>
              <ode/>
              <bullet/>
            </contact>
          </surface>
        </collision>
      </link>
      <pose>0.0 0.0 0 0 0 0</pose>
    </model>
"""

            world_end_content = """    <physics name="default_physics" default="0" type="ode">
      <gravity>0 0 -9.8066</gravity>
      <ode>
        <solver>
          <type>quick</type>
          <iters>10</iters>
          <sor>1.3</sor>
          <use_dynamic_moi_rescaling>0</use_dynamic_moi_rescaling>
        </solver>
        <constraints>
          <cfm>0</cfm>
          <erp>0.2</erp>
          <contact_max_correcting_vel>100</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>250</real_time_update_rate>
      <magnetic_field>6.0e-6 2.3e-5 -4.2e-5</magnetic_field>
    </physics>
  </world>
</sdf>
"""

            world_content = world_start_content + model_content + world_end_content

            with open(world_file_path, 'w') as file:
                file.write(world_content)

            self.report({'INFO'}, "Files exported successfully")
            return {'FINISHED'}

def menu_func_export(self, context):
    self.layout.operator(ExportAnimation.bl_idname, text="Export model to Gazebo")

def register():
    bpy.utils.register_class(ExportAnimation)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(ExportAnimation)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
