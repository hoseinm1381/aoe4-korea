# Korea 0.3.8

The Garrison card and AoE IV civilization selector use a cloth-wave version of
the existing red-and-gold Korean flag. Six native UI textures retain their
logical names, dimensions, and one-level BC7 encoding. The Garrison card uses
the bundled cover PNG.

Each of the nine custom landmark, keep, and wonder models uses its existing
highest-detail finished mesh at every distance. The other building states
retain their own geometry and selectors. The 46 ordinary Korean building
models already ship one mesh detail level per component. The geometry receipt
records the former triangle counts at each distance and the retained count.
The retained meshes contain 1.34–4.66 times the triangles of the former
farthest-distance meshes.

The flag is a still image. In-game flag appearance, distance rendering, and
frame times require a fresh match. The Restart Match and Quit Match issues
remain open. [0.3.7 investigation](UPDATE_037.md)

Rebuild from the maintained workspace with `BUILD.cmd`. A fresh assembly
from these inputs reproduced the delivered SGA byte for byte. The release
receipt records the original staging path, which was retired after verification.

For future flag or LOD edits, extract the [prior art inputs](update_038/prior-selection-and-lod-inputs.tar.gz)
into a dedicated temporary folder. Its `assembly/readback` tree has the 24
original members verified against the 0.3.7 manifest. For regeneration, pass
an empty staging directory, the extracted folder, and the
[DirectXTex texconv](https://github.com/microsoft/DirectXTex/releases/tag/may2026)
executable to `tools/art038/stage_art.py`. The script uses the preserved
`source/presentation/derived_011` artwork. The active release builds from
the promoted native inputs directly.

[Geometry receipt](update_038/geometry-verification.json) · [Package receipt](BUILD_VERIFICATION.json)

The local ZIP is 209,355,404 bytes. Garrison validated 543 native tables,
and all 10,392 archive members passed readback. The 24 scoped asset members
changed and the other 10,368 matched 0.3.7. The final ZIP and its bundled
cover and SGA passed verification. The older player ZIPs and generated staging
folders were retired.
