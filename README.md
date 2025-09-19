# Houdini Bevy Toolbox

The Houdini Bevy Toolbox is a set of utilities that connects SideFX Houdini with the Bevy Game Engine.
It streamlines the workflow of exporting assets, cameras and light data from Houdini into Bevy projects.

## Features

* Bevy Project Creator: Generate a new Bevy project directly from Houdini using the toolbox panel.
* Scene Export: Export Houdini geometry, light, and camera data into JSON/GLTF formats for direct use in Bevy.
* Custom Node Tab: Adds a Bevy tab to supported Houdini nodes (geo, camera, light) for quick integration settings.
* Python Panel UI: Provides tools for creating Bevy projects, running Bevy inside Houdini.

## Installation

1. Clone or download this repository into your Houdini preferences folder.
   Example:`git clone https://github.com/yourusername/houdini-bevy-toolbox.git`
2. Copy the **`bevy_toolbox.json` file into your Houdini** `packages` folder:

   * Windows: Documents/houdini21.0/packages/
   * macOS: ~/Library/Preferences/houdini/21.0/packages/
   * Linux: ~/houdini21.0/packages/
3. Inside the **`bevy_toolbox.json`, set the** `BEVY_TOOLBOX` environment variable to the full path of the toolbox folder.
4. Restart Houdini. A Bevy Toolbox panel should now be available.

## Usage

1. Open Houdini.
2. To open the Bevy Toolbox panel:
   * Right-click on the name of any existing pane (e.g., Network, Parameters, Geometry Spreadsheet).
   * In the context menu, go to ****Misc** →** ****Python Panel** → select** **Bevy Toolbox** .
3. In the Bevy Toolbox panel, click **Create Bevy Project** .
   * This automatically creates the required configuration node(s).
4. Any new ****geometry** ,** **camera** , or ****light** nodes will now include a** **Bevy Enable** checkbox in their parameters.
   * The checkbox is enabled by default.
   * You can disable it for nodes you don’t want to export.
5. Use the panel to export the scene.

## Requirements

* Houdini 21.0+
* Rust & Cargo installed
* Bevy 0.16 or later

## Roadmap

* Support for materials export
* Better error reporting inside Houdini panel
* Export instances (geometry instancing for optimization)
* Live reload: sync changes from Houdini directly into Bevy without restarting
* COPs integration (e.g., procedural texture export, lightmap baking, post-processing)
* APEX integration (rigging and animation support)

## Notes

* **Current structure** : All exports are managed at the **`/obj` level** . This works for now and keeps things simple.
* **Future structure** : In the long run, using **Solaris (USD stage)** could be much more flexible, especially for:
  * Large scene assembly
  * Cross-application workflows (Houdini, Blender, Maya)
  * Substance and other DCC integrations (which already support USD)
* **Bevy limitation** : Since Bevy does not yet support USD natively, even with Solaris we would still need to export **GLTF** for game engine usage.
* This design decision may change as Bevy and USD support evolve.

## Contributing

Contributions are welcome:

1. Fork the repo
2. Create a new feature branch
3. Submit a pull request
