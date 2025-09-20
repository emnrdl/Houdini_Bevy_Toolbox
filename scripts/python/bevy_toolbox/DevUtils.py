import hou
import os
import subprocess
import shutil
from pathlib import Path
from PySide6 import QtCore
from PySide6.QtGui import QIcon, QScreen
from PySide6.QtWidgets import(
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QFileSystemModel,
    QTreeView,
    QHBoxLayout,
    QStackedLayout,
    QPushButton,
    QTabWidget,
)

class CreateBevyProject(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Create Bevy Project")
        self.setGeometry(100, 100, 600, 140)
        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        layout = QVBoxLayout()

        
        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText("Project Name")

        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("Project Directory")
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self.browse_directory)

        self.create_project_button = QPushButton("Create Project")
        self.create_project_button.clicked.connect(self.create_project)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Project Name:"))
        row1.addWidget(self.project_name_edit)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Project Directory:"))
        row2.addWidget(self.dir_edit)
        row2.addWidget(btn_browse)
        layout.addLayout(row2)

        layout.addWidget(self.create_project_button)

        #align top
        layout.setAlignment(QtCore.Qt.AlignTop)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self._center_on_houdini_screen()
        self.show()
    

    def browse_directory(self):
        start = self.dir_edit.text().strip() or "$HIP"
        print("Starting directory:", start)
        chosen = self._houdini_choose_directory(
            start_dir=start,
            title="Select Bevy Project Directory"
        )
        if chosen:
            self.dir_edit.setText(chosen)

    def create_project(self):
        project_name = self.project_name_edit.text().strip()
        project_dir = self.dir_edit.text().strip()
        if not project_name:
            hou.ui.displayMessage("Please enter a project name.")
            return
        if not project_dir:
            hou.ui.displayMessage("Please select a project directory.")
            return

        project_path = Path(hou.expandString(project_dir)) / project_name
        if project_path.exists():
            hou.ui.displayMessage(f"Directory already exists:\n{project_path}")
            return

        cargo = shutil.which("cargo") or str(Path("/Users/emnrdl/.cargo/bin/cargo").expanduser())
        print("Using cargo at:", cargo)

        try:
            subprocess.run(
                [cargo, "new", "--bin", project_name],
                cwd=project_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False
            )
            subprocess.run(
                [cargo, "add", "bevy"],
                cwd=str(project_path),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False
            )
            subprocess.run(
                [cargo, "add", "bevy_houdini_loader"],
                cwd=str(project_path),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False
            )

            # generate basic main.rs
            main_rs_path = project_path / "src" / "main.rs"
            main_rs_path.parent.mkdir(parents=True, exist_ok=True)
            with open(main_rs_path, "w") as f:
                f.write("""use bevy::prelude::*;
use bevy_houdini_loader::prelude::*;
fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .insert_resource(HoudiniImportSettings {
            json_path: "assets/output.json".into(),
        })
        .add_plugins(HoudiniImportPlugin)
        .run();
}
""")

            # create bevy_config node
            bevy_config = hou.node("/obj").createNode("Bevy_Config", project_name + "_config")
            bevy_config.parm("project_folder").set(str(project_path))

            # create basic scene
            box_geo =hou.node("/obj").createNode("geo", "cube").createNode("box")
            box_geo.parm("ty").set(0.5)
            grid_geo = hou.node("/obj").createNode("geo", "grid").createNode("grid")
            light_1 = hou.node("/obj").createNode("hlight::2.0", "light1")
            light_1.parm("light_colorr").set(1.0)
            light_1.parm("light_colorg").set(0.5)
            light_1.parm("light_colorb").set(0.0)
            light_1.parm("light_intensity").set(5.0)
            light_1.parm("tx").set(2.0)
            light_1.parm("ty").set(2.0)
            light_1.parm("tz").set(2.0)
            cam_1 = hou.node("/obj").createNode("cam", "camera1")
            cam_1.parm("tx").set(5.9)
            cam_1.parm("ty").set(4.0)
            cam_1.parm("tz").set(14.0)
            cam_1.parm("rx").set(-15.0)
            cam_1.parm("ry").set(25.0)
            cam_1.parm("rz").set(0.0)
            
            # save houdini scene to the new project folder
            hou.hipFile.save(str(project_path / "houdini" / "scene_v0001.hip"))
            
            hou.ui.displayMessage(f"Creating project at:\n{project_path}")
        except subprocess.CalledProcessError as e:
            hou.ui.displayMessage(f"Failed to create project:\n{e.stderr}")
            return

        # Show success message with option to open folder
        result = hou.ui.displayMessage(
            f"Project created at:\n{project_path}",
            buttons=("Open Folder", "OK"),
            default_choice=1,
            title="Success"
        )
        if result == 0:
            if os.name == 'posix':
                os.system(f'open "{project_path}"')
            elif os.name == 'nt':
                os.startfile(project_path)


        self.close()

    def _center_on_houdini_screen(self):
        main_win = hou.qt.mainWindow()
        if not main_win:
            return

        screen: QScreen = main_win.screen()
        if not screen:
            return

        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)

    @staticmethod
    def _houdini_choose_directory(start_dir=None, title="Select target directory"):
        """Open Houdini's built-in file chooser in directory mode."""
        path = hou.ui.selectFile(
            start_directory=start_dir or "$HIP",
            title=title,
            file_type=hou.fileType.Directory,
            chooser_mode=hou.fileChooserMode.Read
        )
        if not path:
            return None
        path = hou.expandString(path)
        return path.rstrip("/\\")  # strip trailing slashes

def show_create_bevy_project():
    parent = hou.ui.mainQtWindow()
    window =getattr(hou.session, '_bevy_create_project_window', None)
    if window is None or not window.isVisible():
        window = CreateBevyProject(parent=parent)
        hou.session._bevy_create_project_window = window
        window.destroyed.connect(lambda *_: setattr(hou.session, '_bevy_create_project_window', None))

    window.show()
    window.raise_()
    window.activateWindow()

def cargo_run():
    # get all bevyconfig node
    bevyconfig_nodes = hou.node("/obj").children()
    bevyconfig_nodes = [node for node in bevyconfig_nodes if hou.hda.componentsFromFullNodeTypeName(node.type().name())[2] == "Bevy_Config"]
    
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
        print(f"Running cargo in {project_folder}")

        cargo = shutil.which("cargo") or str(Path("/Users/emnrdl/.cargo/bin/cargo").expanduser())

        env = os.environ.copy()
        env["RUST_LOG"] = "info"          # Bevy logları
        env["RUST_BACKTRACE"] = "1"       # panik olursa stack trace
        env["WGPU_BACKEND"] = "metal"     # macOS için garanti


        proc = subprocess.Popen(
            [cargo, "run"],
            cwd=project_folder,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=False
        )

        for line in proc.stdout:
            print("[cargo]",line, end="")
        print("[Bevy] exit code:", proc.wait())


def open_project_in_vs_code():
    # get all bevyconfig node
    bevyconfig_nodes = hou.node("/obj").children()
    bevyconfig_nodes = [node for node in bevyconfig_nodes if hou.hda.componentsFromFullNodeTypeName(node.type().name())[2] == "Bevy_Config"]
    
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
        print(f"Opening VS Code in {project_folder}")

        code = shutil.which("code") or str(Path("/usr/local/bin/code").expanduser())
        if not Path(code).exists():
            hou.ui.displayMessage("VS Code command line tool 'code' not found.")
            return

        try:
            subprocess.run(
                [code, project_folder],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False
            )
        except subprocess.CalledProcessError as e:
            hou.ui.displayMessage(f"Failed to open VS Code:\n{e.stderr}")
            return

def print_node_type():
    """Print type of the selected node"""
    for each in hou.selectedNodes():
        print(each.type().name())
        print(each.path())
        print(each.name())
        print(each.type())
        print(hou.hda.componentsFromFullNodeTypeName(each.type().name()))
    # node = hou.selectedNodes()
    # if len(hou.selectedNodes()) == 0:
    #     hou.ui.displayMessage("No node selected")
    #     return
    # elif len(hou.selectedNodes()) > 1:
    #     hou.ui.displayMessage("Please select only one node")
    #     return
    # else:
    #     print(node[0].type().name())
    #     return
    