# NYRA — concept-led recovery decision

15 November 2026. **Planning/reference preparation only. Waiting for user approval before downloads or 3D generation.**

## Decision: A — replace the character mesh

The approved image is the visual authority. Its printed phrases, including “predicted result” and “game-ready for rigging,” are labels inside concept art, not evidence that a corresponding 3D asset exists or instructions to start rigging.

The current Rain-derived model is not close enough to this target. Phase 3 revision 4 improved adult proportions but still has a generic stylized face, simplified eyelids/lips, solid sculpted hair, a conventional high-neck bomber, and basic fitted garments. It lacks the approved face identity, loose face-framing hair, off-shoulder jacket construction, crop-top neckline, purple design language, gloves and accessory system. Recoloring it or adding accessories would not solve the underlying anatomy and design gap. The latest trouser revision also remains an unfinished fitting trial.

**Salvageability:** technically editable; unsuitable as the primary visual foundation for this approved target. Replacing the face, scalp, hair, outfit and much of the proportion design while retaining Rain would effectively be a new character anyway. Preserve the old mesh as a technical/scale reference only. Do not use it as an appearance reference or reuse its GLB as a retexturing target.

Keep the Phase 2 checkpoint, interrupted Phase 3 source and scripts, neutral render cameras, viewer, GLB validation/export infrastructure, texture-baking automation and useful material-node recipes. New raw generations go in a separate recovery directory. No previous files are deleted or overwritten.

## Reference authority and supplied files

1. `approved-concept.png` — unchanged user-supplied source of truth.
2. `reference-set/01-front-a-pose.png` — derived near-A-pose, full-body front; primary generation image.
3. `reference-set/02-rear-a-pose.png` — matching rear; secondary generation image.
4. `reference-set/03-left-profile.png` — modeling and silhouette check; not an extra input to the verified front/back wrapper.
5. `reference-set/04-face-front.png` — facial sculpt/identity reference; not a substitute for full-body generation input.

These four references were made with the built-in imagegen tool from the approved concept. Prompts are saved under `prompts/`. They are **2D interpretations, not Blender renders or a geometrically exact turnaround**. The approved board overrides any inferred detail. Reference QA and unresolved details are in `REFERENCE_LOCK.md`. Review these derivatives before generation; do not silently promote them above the master.

## Exact recovery sequence after approval

1. **Lock references and prepare masks.** Confirm face, neckline, off-shoulder jacket position, purple panel paths, pouch handedness and sneaker design against the master. Inspect front/rear cutout masks at hair, fingers, sleeves and shoelaces. Align head/sole baselines and overall scale; do not independently stretch body proportions. Keep side/profile and portrait for sculpting. Do not feed the collage, text or old cartoon to Pixal3D.
2. **Generate new geometry in AssetFurnace/Pixal3D.** Use the front + back route, 12 sampling steps, initial seed 42, then a second candidate with seed 1337 only for comparison. Preserve raw GLB, textures, provenance, `.shape.bin` if emitted, `.mvinput` and `.svviews` camera/image sidecars. Run generation only: no automatic rig, animation, aggressive decimation or game integration. Proposed commands are in `generation-recipe.md`; none has been executed.
3. **Reject weak candidates before cleanup.** Compare front, side, rear and 3/4 clay and textured renders against the approved board. Inspect facial planes/eye placement, hands, limbs, waist/hips, jacket-arm separation, hair/torso separation and shoe volumes. A convincing front texture over incorrect geometry fails. If both candidates are structurally poor, stop seed churn and switch to a fresh adult anatomical foundation plus bespoke face/outfit sculpt; do not return to cosmetic Rain edits.
4. **Blender reconstruction.** Use the best generated volume as a starting point, not final production topology. Rebuild the face/eyelids/lips and separate eyeballs as needed; create clean face-framing hair and a controlled ponytail with purple strands; separate/rebuild crop top, dropped jacket, leggings, gloves, pouches, straps and shoes. Restore clean garment boundaries and functional thickness. Preserve raw input in a disabled reference collection. Retopologize for useful deformation loops; create intentional UVs; rebake and author PBR material detail. Pixel Match may help base color before geometry/camera changes, but cannot repair anatomy or replace proper materials.
5. **Visual review gate.** Deliver actual Blender views and close-ups with neutral lighting, plus gameplay-distance rear/3/4 views. Compare against the master, including an untextured/clay pass. No premium-quality approval based on successful scripts, triangle count, texture projection or a single flattering render.
6. **Later phases only.** After visual approval: rig and test running/sliding/jumping, jacket/pony/pouch clearance, then optimize hidden geometry, LODs, material count and texture sizes against measured game/device budgets. Rigging and integration are not part of the present approval request.

## Verified local pipeline / current prerequisite

Read-only inspection of `/Users/dharaksh/image-to-3dlab`, checkout `52b8cf5`, confirms `scripts/pixal3d_generate.py` supports `--back`, `--seed`, `--steps 12`, background matting and raw GLB output. Its built CLI and single-view weight set are present. **The front/back multi-view weight set is incomplete: nine required files are missing.** No weights were downloaded. Readiness checks inspect files only; they do not certify successful inference or image fidelity. Details: `local-pipeline-readiness.json`.

The wrapper stages front/back model inputs at 768 pixels while retaining larger reference images for projection, and requests 1024 generation resolution. Side/face views are for manual review and reconstruction; arbitrary extra-view projection is unsupported by the inspected Pixel Match workflow. Pixel Match changes base color, not geometry. Preserve its cameras and compare its result against raw texturing before choosing it.

Sources: local `scripts/pixal3d_generate.py` and `docs/pixel-match.md`; [official AssetFurnace repository](https://github.com/Bingeljell/image-to-3dlab), [Pixel Match documentation](https://github.com/Bingeljell/image-to-3dlab/blob/main/docs/pixel-match.md). Local inspected behavior takes precedence over newer upstream marketing claims.

## Approval requested next

Approve the replacement strategy and the derived reference set, then authorize completing the missing multi-view weights and making the first two raw candidates. This approval is requested because the user explicitly required a stop at recovery planning. It is not a tool or skill-imposed permission requirement.
