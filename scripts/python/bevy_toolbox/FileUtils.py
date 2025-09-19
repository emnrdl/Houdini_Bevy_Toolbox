import os
import hou

def open_file_location():
    # get houdini current directory
    current_dir = hou.hipFile.path()
    name = hou.hipFile.basename()
    remove_name = current_dir.replace(name, "")
    if os.name == 'posix':
        os.system(f'open "{remove_name}"')
    elif os.name == 'nt':
        os.startfile(remove_name)