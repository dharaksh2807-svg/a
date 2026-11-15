# Asset licensing and provenance

Checked 15 November 2026. This repository contains multiple licensing scopes; there is deliberately no blanket license that reassigns upstream rights.

## Rain — acquired, included

**Credit:** Rain Rig (CC) Blender Foundation | studio.blender.org

- Source: https://studio.blender.org/characters/rain/v3/
- License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/); local legal text: `references/licenses/CC-BY-4.0.txt`.
- Author/publisher credit: Blender Foundation / Blender Studio; the page publisher is Demeter Dzadik. Retain any additional notices in the `.blend`.
- Original files: `source/blender/rain/rain_v3.2.blend` and adjacent `textures/*.png`, copied byte-for-byte from the official archive.
- Provenance and SHA-256 for every included source file: `references/licenses/rain-manifest.json`.
- Modifications to originals: none. Official archive folder says v3.3 while its blend filename says v3.2; these are the actual upstream labels.

**Derived works:** `renders/rain-foundation-{front,rear}.png` use new camera/lighting and capped subdivision for inspection. `source/blender/rain-geometry-study.blend` and `exports/rain-geometry-study.glb` evaluate the source meshes into static geometry, omit cornea/eye-dot objects, remove the rig/embedded scripts, and replace appearance with one neutral clay material. These derivatives retain Rain's CC BY 4.0 attribution and notices. They are not original NYRA character geometry.

Carry the source credit, license link and changes notice into future model metadata, distributed asset documentation and in-game credits. Do not imply Blender endorses Metro Runner. Preserve CC BY rights for the covered asset; do not apply additional legal/technical restrictions to that material. The application code is a separate work.

The original `.blend` includes embedded scripts. Their contents and any license headers are preserved in the untouched source; this asset-level record does not override script-specific terms. Evaluation uses `--disable-autoexec`.

## Original concept material

`references/concepts/runner-concepts.png` was created for this task with the built-in imagegen tool on 15 November 2026. No third-party reference image was provided. Exact prompt: `references/concepts/generation-prompt.txt`. It is an AI-generated visual proposal, not photography, a 3D render, or a third-party reusable base mesh. No claim of exclusive copyright or trademark clearance is made. The original double-dash/back-panel motif should undergo normal identity review before commercial branding.

## Project-authored material

The project scripts, viewer, documentation and environment-test cube were created for this task. No broad open-source license is imposed on the user's new project; the user can choose one later. This does not restrict the separately licensed upstream materials.

## Software dependencies

- Three.js 0.187.0: MIT, https://github.com/mrdoob/three.js . Installed by lockfile; bundled license under `node_modules/three/LICENSE`. Retain the MIT notice when distributing a built viewer containing the library.
- Khronos glTF-Validator 2.0.0-dev.3.10: Apache-2.0, https://github.com/KhronosGroup/glTF-Validator . Development validation dependency; installed package retains its license.
- Blender: GPL software, not relicensing all art made with it. No Blender executable is redistributed here.

## Researched, not included

MPFB core assets: CC0; add-on code: GPL. Blender Human Base Meshes: CC0. VRoid: proprietary preset license with commercial permissions and per-item exceptions. Ellie pose library: CC BY. Mixamo: commercial project use allowed according to Adobe's FAQ; no animation files downloaded and no raw-file redistribution assumed. Exact sources and caveats are in `ASSET_RESEARCH.md`.

No purchased assets, unauthorized mirrors, scraped fashion photography, or third-party character concept sheets are included.

## Phase 2 derivatives — 15 November 2026

The packed NYRA blend, NYRA GLB, skin/eye atlases and all Phase 2 renders adapt Rain geometry and/or textures. Credit: **Rain Rig (CC) Blender Foundation | studio.blender.org**, source https://studio.blender.org/characters/rain/v3/ , license https://creativecommons.org/licenses/by/4.0/ . Changes include face/body reshaping, new brows and ponytail, costume construction/refitting, material changes, texture baking and geometry reduction. Preserve this notice with distribution. Original source bytes remain unchanged.

`textures/nyra/technical-weave.png` is a deterministic original procedural textile texture generated in Blender with seed 218. The other Phase 2 PNG maps are actual Blender emission bakes from the model's material nodes. They are not generated concept images. New project-authored parts do not remove the underlying attribution obligations.
