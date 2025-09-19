import hou

node = kwargs["node"]
ptg = node.parmTemplateGroup()

if ptg.find("bevy_tab") is None:
    bevy = hou.FolderParmTemplate("bevy_tab", "Bevy", folder_type=hou.folderType.Tabs)
    bevy.addParmTemplate(hou.ToggleParmTemplate("bevy_enable", "Enable Bevy", default_value=True))
    ptg.append(bevy)
    node.setParmTemplateGroup(ptg)