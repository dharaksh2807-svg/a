# Browser verification

15 November 2026. In-app browser, local loopback URL `http://127.0.0.1:8765/viewer/`.

- Page loaded concept art and both Rain render images.
- Default GLB loaded: **16 rendered mesh primitives, 76,974 triangles, one material, zero skinned meshes and zero clips**. Export script created 18 objects; empty/masked surfaces do not become rendered GLB meshes.
- Rear button showed the back; Front button showed the face. Wireframe changed the geometry rendering and checkbox state.
- Switching to the environment test showed one mesh, 12 triangles and the explicit environment-only label.
- No browser errors/warnings were present during the inspected default and wireframe states.
- Layout was inspected at the browser's existing narrow viewport; controls wrap and content remains readable.

Animation playback and local-file chooser behavior are implemented but not exercised with a separate animated asset. No claims are made for compressed Draco/KTX2 files, mobile GPU performance or finished character deformation. Screenshots are evidence of the static study, not NYRA production completion.

Saved final browser screenshot: `evidence/viewer-study.jpg`.
