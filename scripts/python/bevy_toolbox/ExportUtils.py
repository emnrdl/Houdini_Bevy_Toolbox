import hou
import os
import math
from PySide6 import QtCore
import json
from pprint import pprint

def export_enabled_bevy_nodes():
    """export all enable_bevy checked geo nodes under /obj"""
    bevy_output_node_name = "bevy_output"
    all_nodes = hou.node("/obj").children()
    bevyconfig_nodes = [node for node in all_nodes if hou.hda.componentsFromFullNodeTypeName(node.type().name())[2] == "Bevy_Config"]
    houdini_json= {}
    houdini_json["units"] = "meters"
    houdini_json["unit_scale"] = 1.0
    houdini_json["entities"] = []
    houdini_json["cams"] = []
    houdini_json["lights"] = []
    if len(bevyconfig_nodes) == 0:
        #show error message
        hou.ui.displayMessage("No BevyConfig nodes found")
        return
    if len(bevyconfig_nodes) > 1:
        hou.ui.displayMessage("Multiple BevyConfig nodes found")
        return
    else:
        bevy_config_node = bevyconfig_nodes[0]
        project_folder = bevy_config_node.parm("project_folder").eval()
        assets_folder = project_folder + "/assets"
        print(f"Exporting to {assets_folder}")
        all_nodes = hou.node("/obj").children()
        geo_nodes = [node for node in all_nodes if node.type().name() == "geo"]
        if len(geo_nodes) == 0:
            hou.ui.displayMessage("No geometry nodes found under /obj")
            return
        bevy_enadled_geo_nodes = []
        for geo_node in geo_nodes:
            bevy_enable_parm = geo_node.parm("bevy_enable")
            if bevy_enable_parm is None or bevy_enable_parm.eval() == 0:
                continue
            else:
                bevy_enadled_geo_nodes.append(geo_node)
        if len(bevy_enadled_geo_nodes) == 0:
            hou.ui.displayMessage("No geometry nodes with Bevy enabled found. Please enable Bevy on geometry nodes to export.")
            return
        objects = ""
        for geo_node in bevy_enadled_geo_nodes:
            # Append geo_node paths to objects list
            geo_path = geo_node.path()
            objects += geo_path + " "

        #create top network box node named bevy_export if not existsing
        if hou.node("/obj/top_bevy_export") is None:
            export_network=hou.node("/obj").createNode("topnet", "top_bevy_export")
            export_network.setColor(hou.Color((0.4, 0.2, 0.8)))
            bevy_task_generator = export_network.createNode("Bevy_Task_Generator", "Bevy_Task_Generator")
            rop_fetch = export_network.createNode("ropfetch", "rop_fetch")
            rop_fetch.setInput(0, bevy_task_generator)
            output_node = export_network.createNode("output", "output")
            output_node.setInput(0, rop_fetch)
            export_network.cookAllOutputWorkItems(include_display_node=True, block=True)    

            rop_gltf = hou.node("/out").createNode("gltf", "Bevy_Gltf_Export")
            rop_gltf.parm("objects").set("`@objpath`")
            rop_gltf.parm("file").set("`@outdir`/assets/`@outname`.gltf")
            rop_gltf.parm("exporttype").set(1) # set to glb

            rop_fetch.parm("roppath").set(rop_gltf.path())

            export_network.parm("cookbutton").pressButton()

        # Export json
        for geo_node in bevy_enadled_geo_nodes:
            geo_name = geo_node.name()
            houdini_json["entities"].append({
                "name": geo_name,
                "output_path": assets_folder + "/" + geo_name + ".gltf"
            })
            #print(f"Exported {geo_name} to {output_path_parm.eval()}")

        cam_nodes = [node for node in all_nodes if node.type().name() == "cam"]
        if len(cam_nodes) != 0:
            for cam_node in cam_nodes:
                
                t, q, s = _world_trs_quat(cam_node)
                # --- Camera intrinsics
                proj_mode = cam_node.parm("projection").eval()  # 0=persp, 1=ortho
                near = cam_node.parm("near").eval()
                far  = cam_node.parm("far").eval()
                resx = cam_node.parm("resx").eval()
                resy = cam_node.parm("resy").eval()
                pixel_aspect = cam_node.parm("aspect").eval()

                data = {
                    "name": cam_node.name(),
                    "transform": {
                        "translation": t,
                        "rotation_quat_wxyz": q,
                        "scale": s,
                    },
                    "projection": "Perspective" if proj_mode == 0 else "Orthographic",
                    "clipping": {"near": near, "far": far},
                    "resolution": {"width": int(resx), "height": int(resy), "pixel_aspect": float(pixel_aspect)},
                }

                if proj_mode == 0:
                    # Perspective: Calculate FOV_y
                    focal_mm = cam_node.parm("focal").eval()  # mm
                    aper_mm_h  = cam_node.parm("aperture").eval()  # horizontal aperture in inches
                    #aper_mm_h = aper_in
                    aspect = (resx / float(resy)) * pixel_aspect
                    aper_mm_v = aper_mm_h / aspect
                    fov_y_rad = 2.0 * math.atan((aper_mm_v * 0.5) / focal_mm)
                    data["perspective"] = {
                        "focal_length_mm": focal_mm,
                        "sensor_width_mm": aper_mm_h,     # Horizontal filmback
                        "sensor_height_mm": aper_mm_v,    # Vertical filmback
                        "fov_y_rad": fov_y_rad,
                        "aspect": aspect,
                    }

                    fstop = cam_node.parm("fstop").eval() if cam_node.parm("fstop") else None
                    focus = cam_node.parm("focus").eval() if cam_node.parm("focus") else None  # meters
                    data["depth_of_field"] = {
                        "fstop": fstop,
                        "focus_distance_m": focus
                    }
                    data["shutter"] = cam_node.parm("shutter").eval()
                else:
                    owidth = cam_node.parm("orthowidth").eval()
                    data["orthographic"] = {
                        "width": owidth,  # world units
                    }

                houdini_json["cams"].append(data)

        light_nodes = [node for node in all_nodes if node.type().name() in ["hlight", "hlight::2.0"]]
        if len(light_nodes) != 0:
            for light_node in light_nodes:
                light_type_val = light_node.parm("light_type").eval()

                intensity = light_node.parm("light_intensity").eval()
                exposure = light_node.parm("light_exposure").eval()
                intensity_photometric = intensity * (2.0 ** exposure)

                color = light_node.parmTuple("light_color").eval()
                color = [color[0], color[1], color[2]]  # RGB

                t, q, s = _world_trs_quat(light_node)

                data = {
                    "name": light_node.name(),
                    "transform": {
                        "translation": t,
                        "rotation_quat_wxyz": q,
                        "scale": s,
                    },
                    "color": color,
                    "intensity_photometric": intensity_photometric,
                }
                if light_type_val == 0:
                    cone_angle = 0.0  # degrees
                    cone_delta = 0.0 # softness
                    conerolloff = 0.0  # rolloff
                    light_type = "Point"
                    data["type"] = "Point"
                    data["spot"] = {
                        "cone_angle_deg": cone_angle,
                        "cone_delta": cone_delta,
                        "cone_rolloff": conerolloff,
                    }
                if light_type == "Point" and light_node.parm("coneenable").eval()==1:
                    cone_angle = light_node.parm("coneangle").eval()   # degrees
                    cone_delta = light_node.parm("conedelta").eval()   # softness
                    conerolloff = light_node.parm("coneroll").eval()   # rolloff
                    data["type"] = "Spot"
                    data["spot"] = {
                        "cone_angle_deg": cone_angle,
                        "cone_delta": cone_delta,
                        "cone_rolloff": conerolloff,
                    }

                houdini_json["lights"].append(data)

        if not os.path.exists(assets_folder):
            os.makedirs(assets_folder)
        json.dump(
                    houdini_json,
                    open(assets_folder + "/output.json", "w", encoding="utf-8"), 
                    ensure_ascii=False,
                    indent=4
                )

def _world_trs_quat(node):
    M = node.worldTransform()

    # Translation
    tx, ty, tz = M.extractTranslates()          # argüman vermeden kullan

    # Scale
    sx, sy, sz = M.extractScales()

    # Rotation (Quaternion): önce 3x3 rotasyon matrisini çıkar, sonra quat'a çevir
    R3 = M.extractRotationMatrix3()             # hou.Matrix3
    q = hou.Quaternion(R3)                      # (w, x, y, z) sırayla erişilebilir

    return (
        [float(tx), float(ty), float(tz)],
        [float(q[0]), float(q[1]), float(q[2]), float(q[3])],  # w,x,y,z
        [float(sx), float(sy), float(sz)],
    )


def create_export_setup():
    pass