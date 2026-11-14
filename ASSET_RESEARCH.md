# Foundation research and ranking

Checked 15 November 2026. Official sources only for reuse decisions. Measurements below are local inspection results where stated; unmeasured figures are explicitly unknown. Ranking reflects visual potential and production effort, not a benchmark of equally customized models.

## 1. Rain v3 — selected

Source: https://studio.blender.org/characters/rain/v3/

Official download: https://studio.blender.org/download-source/files/ee/a7/eea73e55dba1cea31c09848df6a794b2-4.zip

**Reuse:** CC BY 4.0. Commercial adaptation and games permitted with attribution, license link and change notices; no endorsement implied. Preserve supplied attribution. [License](https://creativecommons.org/licenses/by/4.0/).

**Available and acquired:** editable Blender file, external PNG textures and embedded CloudRig UI. Archive label is Rain v3.3, contained file `rain_v3.2.blend`; file metadata reports Blender 4.1.23. Official page lists 4.1+; opening, inspection and static rendering passed on 5.2.3. Full animation/control compatibility is untested with auto-execution disabled.

**Measured complexity:** 20 `GEO-` mesh datablocks total 100,752 base triangles before modifier evaluation; head 6,395 vertices / 12,634 triangles and 25 shape keys; body 10,256 vertices / 20,462 triangles and 72 shape keys. Rig has 2,166 bones, 392 marked deform, 2,788 constraints, B-Bones up to 16 segments and 764 counted drivers. Counts include source variants/hidden geometry; the static export evaluates masks/mirrors and omits cornea/eye dots, producing 76,974 triangles.

**Visual assessment:** inspected real front/rear renders show appealing face planes, sculpted hair, clean hands and cohesive anatomy. The existing youthful head proportions and casual outfit do not yet meet NYRA's adult identity or sport-luxe wardrobe. Existing topology and face articulation are a stronger start than a newly generated generic body.

**Export difficulty: high.** Lattices, corrective smoothing, shape-key drivers, B-Bones, procedural materials and UDIM skin textures need deliberate conversion. Simply selecting “deform bones only” leaves hundreds of bones and does not reproduce Blender-only deformation.

**Customization:** medium-high art effort plus a focused rig/export spike. Preserve a cinematic authoring copy; create a dedicated linear deform skeleton, transfer/refine weights, bake animation, replace facial driver behavior with a small game-safe morph set, and atlas textures. Static clay export is proven; production skinned export is not. Greatest benefit is existing face/topology quality; greatest risk is conversion cost and a recognizable unmodified Rain face.

## 2. Blender Studio Human Base Meshes + custom sculpt/Rigify

Source: https://www.blender.org/download/demo-files/#assets

Official archive: https://mirror.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip

**Reuse:** official asset card lists CC0; commercial use/modification allowed, attribution not required. Card credits Blender Studio and community contributors. Keep that provenance voluntarily. The separate Ellie pose library on the same page has a different license.

**Files/compatibility:** editable Blender asset bundle v1.4.1, advertised 49 MB, Blender 4.2 LTS or newer. Researched, not downloaded or locally tested in this phase. Individual topology counts, UV readiness and shape keys remain unmeasured. Do not treat the archive size as geometry complexity.

The official archive URL was checked with an HTTP HEAD request: it redirected to a Blender-selected mirror and returned 200 with a 50,643,039-byte ZIP. Headers are retained in `qa/evidence/base-mesh-download-headers.txt`; asset contents were not downloaded.

**Visual assessment:** purpose-built topology is a credible editable anatomy starting point; a basemesh is not a finished attractive face. Original sculpt, hair, wardrobe, texturing and rigging remain required. No finished animation solution is assumed. Fit Rigify or a custom control rig, then use a separate deform skeleton for GLB.

**Export difficulty:** moderate once UVs, weights and PBR materials exist; lower legacy-rig burden than Rain, greater art workload. Advantages: license simplicity and maximum identity freedom. Limitations: no proven polished face/materials for NYRA and more manual production time. Best fallback if Rain's face/rig adaptation spike fails.

## 3. MPFB 2 — anatomy and rigging fallback

Source: https://github.com/makehumancommunity/mpfb2

Documentation: https://static.makehumancommunity.org/mpfb.html

Licenses: https://github.com/makehumancommunity/mpfb2/blob/master/LICENSE.ASSETS.md and https://github.com/makehumancommunity/mpfb2/blob/master/LICENSE.CODE.md

Core meshes/targets/skins are CC0; modification, sale and commercial games permitted without attribution. Add-on code is GPL, a separate scope from generated assets. Community clothing, hair and other third-party assets require individual checks. [Official licensing FAQ](https://static.makehumancommunity.org/mpfb/faq/can_i_sell_models.html).

Editable output is native Blender geometry plus configurable targets/assets. Repository requires Blender 4.2+. Not installed here; no local compatibility or generated mesh counts claimed. Geometry varies with proxies, body parts and subdivision; measure the selected output rather than quoting one universal polygon count.

Useful for controllable adult proportions and repeatable generation. Facial identity and stylization still require sculpting and art direction; unmodified generated humans are not the quality target. [Rig options](https://static.makehumancommunity.org/mpfb/docs/characters/rig.html) include GameEngine, default, Mixamo and Rigify. [Export guidance](https://static.makehumancommunity.org/mpfb/docs/exporting/index.html) calls for simplified materials and removal/baking of helper logic.

GLB difficulty is medium with a GameEngine rig and simple PBR materials; higher with complex skin shaders. Customization effort is high for the desired face, hair, shoes and fitted fashion. Advantage: automation and body controls. Limitation: more polish work than Rain. Core assets remain viable; the community homepage reports disrupted asset-browsing services, so do not depend on finding arbitrary community clothing.

## 4. VRoid Studio — viable but stylistically weaker alternative

Source: https://vroid.com/en/studio

Terms guidance: https://vroid.com/en/studio/guidelines

Free proprietary creation tool; built-in assets are **not CC0**. Default assets without special clauses may be modified and used commercially, including games; third-party items retain separate terms. No general attribution condition is stated for standard output in the cited guidelines, but selected presets must be checked. Do not assume rights to another creator's avatar.

Editable `.vroid` source and VRM export; external mesh editing needs a suitable VRM import pipeline. Humanoid skeleton, expressions and hair bones are useful; triangle/material counts depend on export reductions and wardrobe. Not installed or locally tested. Blender compatibility depends on the chosen VRM importer, not VRoid alone.

Stylized faces are quickly attractive within an anime aesthetic, but NYRA needs broader facial planes and sport-luxe tailoring. VRM/MToon and spring bones require conversion or runtime support; renaming `.vrm` to `.glb` is not a material/animation conversion. Moderate-high customization and export effort. Lower fit to the intended art direction than the first three approaches.

## Rigging and animation resources

| Resource | Verified terms and access | Practical fit |
|---|---|---|
| [Rigify](https://docs.blender.org/manual/en/latest/addons/rigify/index.html) | Official manual lists GPL and bundled availability; no extra purchase. Not enabled or tested here. | Modular control rig; mesh fitting/skinning still required. Generated rigs can operate without the generator. Export constraints must be baked. |
| Rain's embedded CloudRig controls | Downloaded inside the official asset; embedded scripts retained intact, never auto-executed in evaluation. See upstream headers for script terms. | Authoring/reference rig only; current tests do not prove IK/FK UI or animation compatibility. |
| [Ellie Pose Library](https://www.blender.org/download/demo-files/#assets) | Official card: CC BY, 24 MB, v2.0.0, Blender 4.0+. Not downloaded. | Pose references tied to Ellie; not a ready NYRA run cycle. Credit and adaptation needed. |
| [Mixamo](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) | Adobe FAQ allows royalty-free commercial games and free access with an Adobe ID. Account access/downloads were not verified; no assets acquired. | Optional biped run/jump/slide starting points, then retarget, remove root drift and polish contacts. Exclude from public source repository until raw-file redistribution terms are checked. Not a project dependency. |
| Original Blender keyframe animation | No third-party animation asset required. | Preferred fallback: author short gameplay-specific loops and transitions on the control rig, bake to deform rig. More animation labor but full control. |

Ellie's character rig itself was not selected: official description identifies a teenager and specifies older 3.3–3.6 compatibility; its identity and version constraints are a poor fit for this adult project. [Official source](https://studio.blender.org/characters/ellie/v1/).

## Decision

Choose Rain's **editable visual foundation**, not its runtime rig. Spend one bounded production spike on an adult face sculpt and shoulder/hip deformation/export comparison. If quality or conversion fails, switch to the CC0 base-mesh approach before building detailed clothes. MPFB remains a practical anatomy/rig alternative, not an automatic default. All three leading approaches are legally viable; only Rain has been acquired and exercised locally.
