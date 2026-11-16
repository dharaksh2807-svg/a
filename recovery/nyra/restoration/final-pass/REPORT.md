# NYRA — final automated recovery attempt

**VERDICT: FAIL — the requested premium visual quality was not achieved.**

This is an unapproved recovery checkpoint, not a successful replacement for Candidate A. Actual Blender comparisons show some improvement, but also new abdominal repair defects. The original is not superseded by this attempt. Stop for independent visual approval. No Phase 4 rigging or Phase 5 integration was started.

## Genuine changes and remaining problems

| Priority | Observed result |
|---|---|
| Abdomen | The original protruding shelf was excised and replaced by a local triangulated surface joined to the cut perimeter. The replacement removes the large folded lip, but its lower join, side transitions, dark seam-like surface artifacts and uneven shading remain visible. This is **not** a seamless anatomical restoration. |
| Face | Eyes/irises are more readable and lip color is more defined in the front view. The original head and facial geometry remain, with modest relaxation and lip reshaping. Reference projection still produces visible artifacts around the eyelids, nose and mouth. Separate anatomical eyes and natural eyelids were not achieved. |
| Hair | Original ponytail and hair silhouette retained; modest geometric relaxation and roughness adjustment. Jagged slabs, holes and fused strands remain. A tested hair-color projection degraded the appearance and was removed from the delivered atlas. No successful strand or hair-card repair is claimed. |
| Body/clothing | Athletic proportions and outfit retained. Coincident vertex welding and conservative local smoothing were applied. Clothing faceting, blurred folds, fused accessories and texture bleeding remain; gloves, belt, straps and pouches are not premium-quality assets. |
| Footwear | Sole colors are more consistent, with a shallow modeled groove and a modest contact adjustment. The sneakers remain bulbous and distorted, especially from the side. Layered construction and convincing ground contact were not achieved. |
| Materials/textures | Skin, hair, fabric and rubber responses are separated. The original 4096-pixel atlas was locally repainted, not upscaled. Abdominal skin is donor infill sampled from Candidate A. Facial detail comes from the existing facial guide; it is not recovered native texture detail. |

## Source and scope

The geometry foundation is exclusively `candidates/candidate-a/renders/original/nyra-review.blend`, corresponding to original `nyra-a.glb`. All original assets and prior checkpoints, including commits `8692317` and `2f9b1d6`, remain untouched. No inference, new candidate, body replacement, or full-character reconstruction was used.

`approved-concept.png` remains the design authority. `inputs/nyra-face.png` was used as the existing facial projection guide. Its derived reference set is marked unapproved in the repository manifest; this pass does not imply that it received separate approval.

## Evidence

The gallery contains matched before/after Cycles renders: front, rear, side, three-quarter, face, abdomen, neutral clay and gameplay distance, plus oblique/clay abdomen and footwear close-ups. Each pair uses identical cameras, studio lighting, exposure, AgX transform, 40 samples and seed 17. The images are actual Blender renders, with no image-generation replacement or retouching of the rendered comparisons.

The Blender master reopens and the GLB reimports. Export contains the character only, with no studio floor, camera, lights or rig. Packed images and finite coordinates were checked. The protected navel/belt region retains all 11,234 sampled original positions within 0.000001 m. These structural checks do **not** establish visual success. See `validation.json` and `gallery-validation.json`.

## Deliverables

- `NYRA-Final-Recovery.blend` — editable, packed, unapproved attempted recovery.
- `NYRA-Final-Recovery.glb` — character-only attempted recovery.
- `index.html` — matched gallery with full-resolution source images.
- `renders/` — all before/after views and comparison sheets.
- `textures/` — delivered local atlas edits and abdominal donor infill.
- Python scripts and JSON records — modifications, source inspection and validation evidence.

**The visual gate remains failed. Independent review is the next step; no further automated recovery, rigging or integration is started.**
