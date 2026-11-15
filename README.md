# NYRA — Urban Velocity

## Phase 3 replacement review

Two independent local Pixal3D front/back candidates, packed Blender scenes, 24 actual renders and an old/A/B comparison viewer are preserved. **Both candidates failed the visual quality gate**: malformed torso surfaces, poor faces, rough hair and distorted shoes remain. Pixel Match comparisons are retained but introduce projection artifacts. No rigging, animation or game integration began.

- [Critical assessment and measured statistics](recovery/nyra/REPLACEMENT_REPORT.md)
- [Actual Blender render gallery](recovery/nyra/renders.html)
- [Candidate A Blender source](recovery/nyra/candidates/candidate-a/renders/original/nyra-review.blend) · [Candidate B Blender source](recovery/nyra/candidates/candidate-b/renders/original/nyra-review.blend)
- Run `npm run viewer` and open http://127.0.0.1:8765/viewer/ for synchronized original/Pixel Match inspection.
- [Raw-output preservation and local-only dense intermediates](recovery/nyra/RAW_OUTPUTS.md)

![Actual old/A/B mesh comparison](recovery/nyra/qa/viewer-comparison.jpg)

## Phase 2 checkpoint

Phase 2 now includes an actual editable character model, ten Blender proof renders and a textured static GLB. Read the [Phase 2 quality report](PHASE2_QUALITY_REPORT.md) for measurements and remaining weaknesses.

![NYRA actual Blender render](renders/phase2/04-three-quarter-front.png)

- Editable source: [nyra-visual.blend](source/blender/nyra/nyra-visual.blend), with packed images.
- Browser asset: [nyra-visual.glb](exports/nyra-visual.glb), with five baked color atlases.
- Face proof: [face close-up](renders/phase2/06-face.png).
- Viewer: run `npm run viewer`, then open http://127.0.0.1:8765/viewer/ . NYRA is the default asset.
- Final rigging, animation/deformation checks, runtime LODs and mobile optimization remain pending.

Rain-derived anatomy is CC BY 4.0; attribution and modification records are in [ASSET_LICENSES.md](ASSET_LICENSES.md). No changes were made to the game repository.

---

# Phase 1 archive

Standalone character project for Metro Runner 3D. **Phase 1: research, art direction and an executable asset foundation.** No changes to the `ss` game repository.

![Three original runner concepts](references/concepts/runner-concepts.png)

The selected direction is NYRA: an adult runner with coral/cream technical outerwear, plum trackwear and a segmented black ponytail. The image above is AI-generated concept art, **not a render of an existing NYRA mesh**.

## Delivered

- Official Rain editable `.blend` and 22 PNG textures, with SHA-256 provenance and CC BY 4.0 attribution.
- Actual front/rear Blender renders of Rain, plus a static clay geometry GLB for inspection.
- Verified Blender save, CPU render, Metal GPU render, Eevee render and GLB export.
- Three concepts, four ranked foundation approaches, licensing and production decisions.
- Independent local viewer with orbit, front/rear, wireframe, rotation, local GLB loading and animation selection for future animated assets.

## Open the work

```sh
npm ci --ignore-scripts
npm run viewer
```

Open http://127.0.0.1:8765/viewer/ . The server is loopback-only. No account or hosted service is needed. Dependencies are pinned; the viewer loads them locally.

Editable upstream source: [`source/blender/rain/rain_v3.2.blend`](source/blender/rain/rain_v3.2.blend). The official v3 URL currently downloads an archive labeled **Rain v3.3** containing this v3.2-named file. Names and bytes are preserved, not silently relabeled. Keep its adjacent `textures` folder.

## Reproduce verification

Set `BLENDER` if it is not on PATH and not installed at the macOS default location.

```sh
python3 scripts/run_environment_audit.py
"$BLENDER" --background --disable-autoexec source/blender/rain/rain_v3.2.blend --python scripts/inspect_asset.py
"$BLENDER" --background --disable-autoexec source/blender/rain/rain_v3.2.blend --python scripts/render_foundation.py
"$BLENDER" --background --disable-autoexec source/blender/rain/rain_v3.2.blend --python scripts/export_foundation_study.py
npm run validate
python3 scripts/verify_project.py
```

For macOS, first run `export BLENDER=/Applications/Blender.app/Contents/MacOS/Blender`. Rendering and export scripts never overwrite the original Rain files. Embedded upstream Python is disabled in these evaluation commands. Cold GPU probes allow 180 seconds by default; override with the `BLENDER_PROBE_TIMEOUT` environment variable.

## Status and next steps

Read [ART_DIRECTION](ART_DIRECTION.md), [ASSET_RESEARCH](ASSET_RESEARCH.md), [ASSET_LICENSES](ASSET_LICENSES.md), [PRODUCTION_PLAN](PRODUCTION_PLAN.md), [ENVIRONMENT_AUDIT](ENVIRONMENT_AUDIT.md) and [QA](qa/README.md).

**Not yet built:** the customized NYRA mesh, final clothes/hair/textures, production game skeleton, animations, LODs and mobile performance validation. The 76,974-triangle clay GLB has no rig and is a foundation study. The test cube is only environment evidence. Neither is a finished NYRA asset.

Actual execution was on the local Mac. No cloud machine was provisioned or verified.

Rain Rig (CC) Blender Foundation | [studio.blender.org](https://studio.blender.org/characters/rain/v3/) — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Changes to inspection derivatives are documented in ASSET_LICENSES.md.
