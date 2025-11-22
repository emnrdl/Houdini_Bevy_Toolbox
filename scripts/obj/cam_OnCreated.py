import hou

node = kwargs["node"]
ptg = node.parmTemplateGroup()

if ptg.find("bevy_tab") is None:
    bevy = hou.FolderParmTemplate("bevy_tab", "Bevy", folder_type=hou.folderType.Tabs)
    bevy.addParmTemplate(hou.ToggleParmTemplate("bevy_enable", "Enable Bevy", default_value=True))
    bevy.addParmTemplate(hou.ToggleParmTemplate("fly_cam", "Enable Fly Camera", default_value=False))
    ptg.append(bevy)
    node.setParmTemplateGroup(ptg)