# Robo-Jack Assembly Explorer

A local Vite + Three.js viewer for the actual Robo-Jack Blender model. Individual visible objects remain separate meshes, with their Blender names and assembly metadata.

## Run

Requires Node.js 22.12+ or a compatible newer version.

```powershell
cd D:\codex+blender\model\web-viewer
npm install
npm run dev
```

Open http://127.0.0.1:5173. For a production build, run `npm run build`; test that build with `npm run preview`. Serve `dist/` using any static web server. Opening `index.html` directly with `file://` will not load JavaScript modules or the GLB correctly.

## Interactions

- Drag to orbit, scroll/pinch to zoom, right-drag to pan.
- Click any mesh, or search the assembly list and select a part.
- Focus, hide/show, or isolate the selected object. Press F to focus and Escape to clear selection/isolation.
- Adjust an object's X/Y/Z position offset in meters. Reset a part or the entire scene.
- Use the exploded view slider, camera presets, wireframe, auto orbit, and grid controls.
- Save an image of the current 3D view.

All changes are browser-local; they do not modify the Blender source. This is an object inspection viewer, not an animation rig or Blender replacement. The snapshot includes the 3D canvas only.

## Updating the asset

`public/models/robo-jack.glb` is exported from `D:\codex+blender\model\robot\blender\current\robot_attachments_repaired.blend`. The export selects only visible robot mesh/curve objects, evaluates modifiers on temporary copies, keeps object identity in glTF extras, and excludes studio lights, ground, references, and hidden obsolete modeling passes. `public/models/manifest.json` records the export contents. The exporter is saved as `export_robot_web.py`; run it from Blender's Python console after reviewing its source/output paths. Source objects remain untouched.

Blender procedural roughness is approximated with static PBR values for glTF. The browser environment and lights are intentionally independent of Blender's studio setup. No third-party concept images are published.

## Verification

```powershell
npm run check
npm run build
npm run test:browser
```

The browser smoke test uses installed Google Chrome on Windows. Set `CHROME_PATH` to use another Chromium executable. Start `npm run dev` before testing; set `TEST_URL` to test another local server. Tests cover model loading, canvas picking, search, isolation, hiding, object offsets, explosion, wireframe, camera focus, PNG download, reset, and mobile overflow. Reports and screenshots are written to ignored `test-results/`.

Dependencies are pinned in package.json and package-lock.json. Fonts are bundled locally. No deployment or Git commit is created automatically.
