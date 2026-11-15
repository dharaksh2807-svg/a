# Preserved inference outputs

Each `candidates/candidate-*` folder retains the original generated GLB, PLY, 4096-pixel base-color image, shape latent, dense postprocess dump, model input views, Pixel Match camera/reference views, generation log and provenance. The wrapper rotates the exported GLB and its saved projection cameras together to glTF +Z front; the PLY and dense intermediates remain in engine coordinates.

The `*.post.bin` dense intermediates exceed GitHub's 100 MiB per-file limit. They remain **locally preserved**, excluded from ordinary Git, with sizes and SHA-256 hashes recorded in `preservation-manifest.json`. No paid storage or LFS service was introduced. The other deliverables can be versioned normally.

`original` Blender scenes contain an unchanged imported mesh under a presentation-only parent transform, packed textures, studio lights and a review camera. `pixel-match` scenes are separate comparisons. No game retopology, rig, animation or manual decimation was added. The generator's own default postprocessing is recorded in its log and the earlier dense dump remains available.
