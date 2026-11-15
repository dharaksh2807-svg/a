# NYRA replacement review — visual gate failed

**Neither candidate is approved as final NYRA.** Both reproduce the broad purple/black outfit and adult silhouette, but fail the required face, hair, garment construction and finish quality. Do not rig, animate or integrate either. The old Rain-derived model and previous checkpoints remain intact.

## What was executed

- Visually checked all four derived references and their cutouts against `approved-concept.png`. Front/rear retain the crop top, dropped purple jacket, ponytail, gloves, belt/pouches and matching shoes. Uniform scaling aligns silhouette height and floor without stretching proportions. Fine hair matting noise, minor seam/emblem differences and ponytail-tip variation remain. Side and face references are manual guides, not extra projection cameras.
- Downloaded the missing official `raven38/pixal3d-q8_0-v1` multi-view flows, reusing installed shared weights and dependencies. No paid services.
- Generated A (seed 42) and B (seed 1337) independently, sequentially on local Metal at resolution 1024 / 12 steps. The queue waited for Messi inference to finish. Generation took about 672 and 503 seconds respectively.
- Preserved raw GLB, PLY, base-color PNG, dense intermediate, shape latent, input views, cameras, logs and provenance. No manual decimation, retopology or rigging.
- Saved packed editable Blender review scenes and actual studio renders: front, three-quarter, side, rear, face, clay, full-body wireframe, close-up wireframe and gameplay-distance presentation. The gameplay view uses the established Metro sun/blue-fill colors. Separate front/rear/face renders compare Pixel Match under identical cameras and lighting.

## Measured mesh data

| | Candidate A | Candidate B |
|---|---:|---:|
| Vertices imported in Blender | 724,640 | 784,002 |
| Triangles | 958,378 | 995,454 |
| Mesh objects / materials / UV layers | 1 / 1 / 1 | 1 / 1 / 1 |
| Base-color and metallic/roughness images | 4096 × 4096 each | 4096 × 4096 each |

These counts do **not** establish visual quality or game readiness.

## Critical findings

| Area | A | B |
|---|---|---|
| Face | Poor eye reconstruction, swollen/smeared lips, identity drift | Poor eyes and mouth; lacks the concept's attractive, resolved anatomy |
| Torso/outfit | Extra raised strip across exposed abdomen; crop-top/body reconstruction conflicts | Similar unwanted abdomen strip and irregular garment boundaries |
| Hair | Thick, torn-looking slabs, holes and irregular hanging strands | Thick violet loops and rough clumps; unsuitable hair construction |
| Shoes | Inflated, distorted soles and blurred panel/lace detail | Especially malformed dark toe/sole protrusions |
| Surface/materials | Visible faceting, smeared fabric, inaccurate skin/hair finish | Same weaknesses; insufficient close-up fidelity |

Both have visible arms, hands, legs and shoes, and recognizable front/rear clothing placement. This does not excuse the defects. Clay exposes unwanted torso relief and rough forms; they are not simply color-map errors. The single imported surface does not provide production-ready separate eyes, garments or deformable hair. Back views and gameplay distance are more forgiving, but do not rescue the failed close-up and construction quality.

## Pixel Match decision

**Retain original generated textures as the default for both candidates.** Preserve Pixel Match variants for comparison only. Pixel Match restores more source-like eyes, neckline details, logos and laces, but introduces projection seams, overlapping facial/necklace details and mismatched painted edges. It cannot repair the torso, hair or shoe geometry. Its trust maps report approximately 15% (A) and 14% (B) of atlas texels strongly replaced; those percentages are not quality scores.

The viewer provides both variants explicitly. No flattering projection-only view is presented as a successful model.

## Pipeline conclusion and next gate

The approved concept remains the target. These two outputs are insufficient as a final character foundation without substantial reconstruction. The runtime warns that this multi-view weight family was validated at four views, whereas AssetFurnace's authorized front/back route supplied two. This is a limitation of this experiment, not proof that all Pixal3D configurations fail.

Do not continue random seeds or cosmetic polishing of these failures. The next meaningful step, **after visual review**, is a controlled rebuild of the head/eyes, torso/top boundary, hair and sneakers with proper editable anatomy and garment separation. Use the approved reference package and retained reconstruction only as spatial guides; evaluate a face/torso sample before committing to the full rebuild. This requires interactive character-art judgment. No such rebuild or subsequent rigging was performed; visual review is pending.

## Files and verification

- [Interactive comparison](../../viewer/index.html) — old NYRA plus A/B, synchronized cameras and texture choices. Serve the repository with `npm run viewer`; open `http://127.0.0.1:8765/viewer/`.
- [Actual render gallery](renders.html) — rendered meshes, not AI concept proof.
- Packed sources: `candidates/candidate-a/renders/original/nyra-review.blend` and equivalent B path; separate Pixel Match scenes alongside.
- `qa/glb-validation-summary.json`: all four GLBs pass glTF validation with zero errors and warnings. This validates file structure, not artistic quality.
- `qa/preservation-verification.json`: checkpoint hashes and unchanged positions/UVs/indices across texture variants.
- `qa/viewer-comparison.jpg`: actual browser proof. Front/rear/side/face synchronization, wireframe and both texture selectors were exercised; no browser console errors observed.
- [Raw-output retention](RAW_OUTPUTS.md): dense `.post.bin` files are preserved locally with SHA-256 manifests; they exceed ordinary GitHub's per-file limit. Other review assets are versioned normally.

**Visual verdict: FAIL — neither candidate meets the approved concept's premium quality bar. Stop for user review.**
