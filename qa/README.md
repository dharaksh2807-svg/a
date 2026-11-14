# Quality assurance

Phase 1 evidence is stored in `evidence/`. Final character acceptance remains open.

## Automated checks

- `python3 scripts/run_environment_audit.py`: separate mandatory core operations and optional Eevee/Metal probes; bounded subprocesses.
- `npm run validate`: Khronos glTF-Validator on both delivered GLBs, fails on validation errors.
- `python3 scripts/verify_project.py`: source hashes, PNG signatures, required artifacts, GLB structure and phase-status checks.

## Visual checks performed

- Generated concept board: all three adult runners have front/rear full-body depictions, coherent broad palettes and distinguishable silhouettes. NYRA chosen; rear-view hair length and small unrequested jewelry require correction. Not a technical turnaround.
- Actual Rain renders: front and back visible, feet/hands within frame, expected face/hair/clothes present, no missing-texture magenta. Original character, not customized NYRA.
- Browser bench: see `browser-checks.md` for observed controls and results. The static GLB has no animations, so clip playback is not certified by this phase.

## Future character gates

Adult identity and distinctness from Rain; shoulder/hip/knee/wrist deformation; no clothing penetration through run/jump/slide; clean planted feet; front/rear readability; 4-weight normalization; explicit units/facing; glTF validation; morph and animation round-trip comparison; target-device load/memory/frame time; license credits in exported metadata and game distribution.
