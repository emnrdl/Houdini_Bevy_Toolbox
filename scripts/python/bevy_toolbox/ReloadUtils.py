import hou

def reload_all_fbx_nodes():
    # Get all the FBX nodes
    fbx_nodes = hou.sopNodeTypeCategory().nodeType('kinefx::fbxskinimport').instances()
    # Loop through all the FBX nodes and reload them
    for node in fbx_nodes:
        node.parm("reload").pressButton()
    hou.ui.displayMessage("All FBX nodes reloaded")