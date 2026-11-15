# Proposed commands — NOT EXECUTED

Run only after the user approves the recovery strategy and reference set.

From `/Users/dharaksh/image-to-3dlab`, complete the missing front/back model set using the installed environment:

```sh
.venv/bin/python scripts/bootstrap_pixal3d.py --multiview
```

After inspecting approved front/rear masks and alignment, create a separate candidate directory and generate raw geometry:

```sh
mkdir -p /Users/dharaksh/Desktop/a/recovery/nyra/candidates
.venv/bin/python scripts/pixal3d_generate.py \
  /Users/dharaksh/Desktop/a/recovery/nyra/reference-set/01-front-a-pose.png \
  /Users/dharaksh/Desktop/a/recovery/nyra/candidates/nyra-seed42.glb \
  --back /Users/dharaksh/Desktop/a/recovery/nyra/reference-set/02-rear-a-pose.png \
  --res 1024 --steps 12 --seed 42 --matte
```

Inspect the automatically saved mattes; reject clipped fingers, hair or shoe boundaries. If corrections are needed, preserve the original PNGs and use inspected RGBA sibling files as the inputs instead. Keep the same approved images and settings for a second candidate, changing only output name to `nyra-seed1337.glb` and seed to `1337`.

The command targets generation only. Do not invoke auto-rig, animation or the whole end-to-end Create pipeline. Keep generated camera/shape/provenance sidecars next to each GLB. Preserve raw outputs before any Finish, Pixel Match or Blender modification. No claim is made that these unexecuted commands will reach the art target.
