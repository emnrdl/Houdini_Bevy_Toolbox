import hou

node = kwargs["node"]
ptg = node.parmTemplateGroup()

if ptg.find("bevy_tab") is None:
    bevy = hou.FolderParmTemplate("bevy_tab", "Bevy", folder_type=hou.folderType.Tabs)
    bevy.addParmTemplate(hou.ToggleParmTemplate("bevy_enable", "Enable Bevy", default_value=True))
    bevy.addParmTemplate(hou.ToggleParmTemplate("instance_point_cloud", "Instance Point Cloud", default_value=False))
    bevy.addParmTemplate(hou.ToggleParmTemplate("instance_geo", "Instance Geometry", default_value=False))
    ptg.append(bevy)
    node.setParmTemplateGroup(ptg)