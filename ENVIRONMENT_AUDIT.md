# Environment audit

Executed 15 November 2026 in Asia/Kolkata. **This is a verified local desktop audit, not a cloud capability claim.** No cloud executor was available in this session and no cloud host was provisioned.

## Observed host

| Item | Verified result |
|---|---|
| OS / architecture | macOS 26.5.2, build 25F84, arm64 |
| CPU / RAM | Apple M5, 10 logical CPUs, 17,179,869,184 bytes (16 GiB) installed unified memory |
| GPU | Apple M5 GPU, 10 cores, Metal 4 reported by macOS |
| Blender | 5.2.3 LTS, hash `e13b728c6880`, official installed app at `/Applications/Blender.app` |
| Python | Host 3.14.7; Blender's embedded Python 3.13.13 |
| Tools | Git 2.55.0, Node/npm and FFmpeg present; exact inventory in `qa/evidence/host.json` |
| Rendering | Actual PNGs created with Cycles CPU, Cycles Metal GPU and Eevee in background mode |
| Repository | HTTPS Git clone of `dharaksh2807-svg/a` succeeded; repository was empty |
| Network | Official Rain page/archive downloaded by curl with normal certificate verification; npm and GitHub reachable |

Memory is installed capacity, not guaranteed free memory under production load. No installation of Blender or paid service was needed.

At the final check, macOS `memory_pressure -Q` reported a **50% system-wide memory free percentage** (raw output in `qa/evidence/memory-pressure.txt`). This is a momentary OS-reported metric, not a reserved 8 GiB allocation.

## Executed tests

`scripts/run_environment_audit.py` invokes isolated background Blender processes. `scripts/smoke_blender.py` creates an explicitly named test cube, saves a real `.blend`, renders PNG and exports GLB. The cube is environment evidence only.

All core operations and both optional engine probes passed. Logs and operation results are in `qa/evidence/blender-{core,eevee,metal}.{log,json}` and `environment-results.json`. Runtime products:

- `source/blender/environment-smoke.blend`
- `renders/environment-cycles-CPU.png`
- `renders/environment-cycles-GPU.png`
- `renders/environment-blender_eevee-default.png`
- `exports/environment-smoke.glb`

First Metal operation took 108.865 seconds. It initially appeared stalled but completed; no termination occurred. The repeated isolated Metal operation took 0.402 seconds. This is consistent with cold initialization/compilation overhead, but the exact internal cause was not diagnosed. Tiny 256px/8-sample timings are not representative production benchmarks.

Rain also opened with auto-execution disabled, was inspected, and produced 768×960 front/rear Cycles CPU images with 24 samples. Inspection render times were approximately 2.7 and 2.0 seconds in that session; see `foundation-renders.json`. Geometry study `.blend` and GLB exports succeeded. Both GLBs passed Khronos validation with zero errors and warnings.

## Exceptions, recovered failures and limits

- Python urllib's default CA setup rejected the Rain HTTPS certificate. System curl succeeded with verification enabled. No certificate checks were disabled; use curl or repair Python's CA configuration for future acquisition.
- Some research-browser requests to Blender sites returned 402/403 despite publicly accessible official downloads. Normal curl obtained the Rain page/archive; no account wall or paywall was bypassed.
- GitHub connector metadata call failed because the connection lacked a required `link_id`. The public repository was verified via the browser and normal Git. Push uses the existing Git credential configuration.
- The first Rain staging script used an operator unavailable in the saved file's context. It was changed to direct Blender data API object creation; final front/rear renders passed.
- Embedded Rain Python remains disabled. Static appearance/geometry success does not certify all CloudRig controls, actions or driver-driven facial behavior.
- The source file uses Blender-only modifiers and UDIM textures. The successful static clay GLB does not establish production skinning/material/animation fidelity.

For a cloud host, execute the same audit and report its own CPU/GPU, memory and render evidence. Apple Metal results apply only to this Mac.
