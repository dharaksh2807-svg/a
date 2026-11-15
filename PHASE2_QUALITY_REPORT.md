# NYRA — Phase 2 visual production

15 November 2026. Actual Blender geometry and rendering; no generated concept image is used as production proof.

## Delivered model

`source/blender/nyra/nyra-visual.blend` is the editable, packed authoring file. The original Rain source remains untouched. The face retains a separate **NYRA adult identity** shape key; the model has editable meshes, curves, garment thickness, subdivision and a localized shoulder smoothing modifier. No final armature was created.

Changes include smaller orbital/eye proportions, cheek and jaw reshaping, a softer lip treatment, tapered fitted brows, brown iris coloration, warm painted skin variation, a revised black hair cap and a new continuous segmented ponytail with copper cuffs. Body proportions and a relaxed A-pose were established geometrically. The outfit includes a constructed cropped bomber, fitted jersey layers, a cream shoulder yoke, rib trims, zipper rails, pocket welts, adapted track pants, outer-calf inserts, a fitted waistband and reworked sneakers with new soles and overlays.

Materials use painted source skin/eye detail, a saved technical weave texture, weave bump, roughness, skin subsurface scattering and modeled trim. Five baked color atlases support the browser asset. The GLB deliberately simplifies Blender-only surface effects; it is not the fidelity reference for close-up skin shading.

## Proof

All files are in `renders/phase2/`:

| File | Evidence |
|---|---|
| `01-front.png` | Full-body front |
| `02-left-profile.png` | Left profile, ponytail attachment and garment depth |
| `03-rear.png` | Rear silhouette and back mark |
| `04-three-quarter-front.png` | Full-body presentation |
| `05-three-quarter-rear.png` | Rear three-quarter |
| `06-face.png` | Actual face close-up |
| `07-garment-detail.png` | Clothing, collar, weave and trim |
| `08-neutral-presentation.png` | Neutral A-pose |
| `09-metro-light.png` | Modern Metro-inspired daylight |
| `10-sneaker-detail.png` | Sneaker construction |

The game-light setup follows a read-only inspection of `ss/src/environment/EnvironmentConfig.ts` (Modern Metro: warm white sun, blue fill and cyan hemisphere) and `ss/src/scene/WorldScene.ts`. Blender lighting and tone mapping are an approximation, not a captured in-game frame. No game files were modified.

## Measured complexity and validation

See `qa/phase2/mesh-statistics.json` for measured source and export counts. The authoring model retains 43,819 base mesh vertices and 83,526 base mesh triangles, plus editable curves. Its evaluated modeling surfaces total 415,040 triangles. This includes hidden anatomy and subdivision retained for editing and close-up rendering.

The static browser review export removes covered anatomy and reduces broad garment surfaces before baking while preserving thin hems, jersey layers and trims. It contains **156,686 triangles**, with **12,073,716 bytes** (11.51 MiB) in the packed GLB. It uses five texture/material groups and has no skins or animation clips. It is **not a mobile runtime budget pass**; LOD construction and final skinning remain separate work.

Source checks pass for fitting revision 6 and verify finite geometry, UV presence, materials, packed images, the editable identity key, absence of external blend libraries and absence of a final rig. Khronos glTF validation reports **0 errors and 0 warnings**, recorded in `qa/phase2/glb-validation.json`. The standalone viewer was visually checked with NYRA selected by default, front/rear controls working and no browser console errors or warnings; `qa/phase2/viewer-nyra.jpg` records the actual textured model. These checks do not certify artistic quality, invisible mesh intersections or future deformation.

## Remaining weaknesses

- The result is a credible editable visual model, but the premium hero-art target still needs an interactive sculpt/tailoring review. Sleeve folds are somewhat regular; hem, collar and underarm transitions can be more finely art-directed.
- Rain's underlying facial and scalp topology remains recognizable. The new proportions, brows, shading, outfit and ponytail establish a different design, but a further face/scalp sculpt could strengthen originality.
- The neutral pose has been inspected; running, sliding and extreme joint bending are not tested. Garment penetration during animation cannot be certified before fitting and weight work.
- The authoring face has an identity shape key, not a finished facial expression system. Its current expression is static.
- Browser atlases retain color detail but omit subsurface scattering, the fine weave bump and the separate refractive cornea. Small metallic trims use simplified PBR shading.
- The source pants still retain some inherited pocket/fold construction. Runtime LODs, skin weights, animation clips and target-phone performance remain unbuilt.

These limitations are not hidden by the renders. Do not treat this delivery as a final rigging or commercial-release approval.

## Reproduce only what is needed

Open the packed authoring blend directly. Rendering: `Blender --background --disable-autoexec source/blender/nyra/nyra-visual.blend --python scripts/render_nyra.py`; use `-- --only 06-face` for one changed view. Static export: `--python scripts/export_nyra_visual.py`. Source checks: `--python scripts/verify_nyra_source.py`.

The saved file is the handoff; **do not rerun the initial builder to continue editing it**. For reconstruction only, the original build is followed by `finish_nyra.py`, `smooth_jacket.py`, `fit_jersey.py` `fit_trims.py` and `correct_final_fit.py` and `fit_sneaker_junctions.py`, in that order. Intermediate scripts record the completed fitting operations. The final pass corrected waistband ray direction, seated back marks and zipper hardware, and fitted the sole envelope to the sneaker uppers.
