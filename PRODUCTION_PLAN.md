# Production plan and phase boundary

Phase 1 establishes direction, provenance, verified tools and an editable foundation. It does not pretend that a customized character has already been modeled.

## Current deliverables

| Requirement | Evidence / status |
|---|---|
| Environment audit | Local host inventory plus executed CPU, Metal, Eevee, save and GLB tests. Cloud execution unverified. |
| Three viable approaches | Rain, CC0 Human Base Meshes and MPFB compared; VRoid evaluated as a fourth. |
| Base acquisition | Official Rain blend + 22 textures, local renders, source hashes. |
| Three concepts and selection | Generated comparison board; NYRA selected with concrete production corrections. |
| Standalone project | This repository; no integration with the game. |
| Preview and viewer | Concept image, Rain renders, validated static clay GLB, interactive local viewer. |
| Licensing | Asset-specific register, upstream license and checksum manifest. |
| Final NYRA | Outside Phase 1; not created or exported. |

## Phase 2 · Identity and export feasibility

Start a new `nyra-authoring.blend` derived from a copy, preserving the untouched Rain folder. Establish roughly 7.25-head adult proportions, distinctive facial planes and hair volume. Render identity studies before tailoring. Rebuild rather than perpetuate Rain's scarf, casual top, jeans and original ponytail silhouette.

Perform a focused export spike before detail work: create a clean deform-only skeleton, normalize scale, transfer weights, compare shoulder elevation, hip flexion, knee bend and wrist twists. Rain's existing B-Bone/lattice deformation is not portable. A separate armature with explicit linear joints is preferred to deleting control bones from the cinematic source. Refit/repaint weights as needed; preserve correct bind matrices.

Bake sample animations onto the new deform bones at 30 fps; remove constraints from the export copy only. Compare Blender and browser poses at multiple frames. Derive a small facial morph set from evaluated expressions, with consistent vertex order. If the adult sculpt or deformation export looks worse than a new CC0 base sculpt, use the ranked fallback early.

## Phase 3 · Wardrobe, hair and materials

Model the cropped bomber with separate outer/inner surfaces where visible; do not use coarse procedural tubes as final sleeves. Sculpt folds around elbows, cuffs and shoulder seams, bake their fine detail. Use low-poly segmented hair clumps and a short secondary chain. Build original sneakers and remove unseen body polygons only in the export copy.

Bake Rain-derived UDIM skin and new materials into runtime atlases. Use Principled-compatible metallic/roughness inputs; convert packed maps intentionally. Bake procedural cloth/skin effects that cannot travel through glTF. Review normal map handedness, color spaces, roughness and appearance under at least two light rigs. No runtime dependency on Blender shaders or Python drivers.

## Phase 4 · Gameplay motion

Author or retarget idle, run, jump, fall, landing, slide, lane-change left/right and stumble. Default to in-place movement; make root-motion clips explicit if later game integration requires them. Lock planted feet, remove root drift, test transition lengths, preserve readable arms from the rear. Use original keyframing if Mixamo account access is unavailable. Secondary hair motion must be baked or explicitly supported by the eventual runtime.

## Phase 5 · Delivery and acceptance

Provisional budgets, to be revised against the real target device/game in the later integration phase:

- LOD0: 25–40k triangles; LOD1: 12–20k; LOD2: 5–10k. These are targets, not current measurements.
- Approximately 60–80 deform joints including simple hands and hair; <=4 normalized weights per vertex.
- Aim for 3–5 material draw groups, a 2K body/outfit atlas and smaller hair/face maps as justified. Prefer opaque geometry; limit alpha overdraw.
- Aim for <=8 MB compressed runtime model plus textures, with measured load time and memory. Current uncompressed static GLB is only a diagnostic.
- Choose texture/geometry compression only after the viewer and integration runtime support the corresponding decoder. The Phase 1 viewer does not support Draco/KTX2.

Validate GLB with Khronos, reimport into a clean Blender scene, compare bounds/scale/morphs/skin and animation timestamps, then inspect in-browser. Test target-phone frame time inside the real scene later; desktop smoke timings do not establish a mobile performance budget.

Deliver editable authoring blend, clean export blend, textures, GLB/LODs, named actions, attribution, hashes and renders. Archive final-art approval images and deformation checks. Keep integration into `ss` separate and explicitly scoped.

## Open issues and recovery

1. **Cloud unverified:** this session exposes a local desktop executor. Re-run `run_environment_audit.py` on a real configured cloud host when available; set `BLENDER` there. Do not transfer Apple Metal assumptions to Linux.
2. **Full Rain rig unverified:** embedded scripts were disabled. Review official embedded UI code and test it in a dedicated authoring session, or keep the independent rig strategy.
3. **No finished adult NYRA mesh:** production sculpt, clothing, hair and all game animation remain necessary; the concept image cannot be exported into geometry.
4. **Mixamo access unverified:** Adobe ID access is optional. Original animation avoids blocking the project or making a public raw-animation redistribution assumption.
5. **Cold GPU startup:** first Metal render took about 109 seconds, later warm render was under a second. Cold probe timeouts are configurable; do not mark GPU broken from a short cold timeout.
