# Korean art sources for the next 0.1.3 candidate

These 152 editable sources were promoted from the owner’s existing Korean art
workspace. All saved files were cold-opened and compared with the originals:
geometry, topology, UVs, weights, rest bones, materials and object transforms
match. Active image paths are relative to this checkout. Shared packed images
were consolidated into `textures/` after byte verification; original 1024-pixel
unit texture masters are retained by content hash. The originals remain intact.

`catalog.json` is the file/texture/provenance index. Original absolute paths and
native-state contracts identify earlier evidence; they are not build dependencies.
Review PNGs, GLBs, Blender backup files, decoded donor manifests and cook caches
were omitted. Native donor resources can be decoded again from the installed
game after checking their recorded identity/hash.

Coverage: 54 human body variants, 18 mounts/cargo, 25 equipment pieces,
46 ordinary building variants and 9 unique buildings/landmarks/wonder.
These files are not yet referenced by the playable mod. See
[the integration status](../../docs/UPDATE_013.md) for the native cook blocker,
qualified pilot export, pending private bindings and next steps.

Open any indexed `.blend` directly. To verify all indexed bytes and the unchanged
runtime source: `python -B tools/art013/check_sources.py` from the repository root.
For a fresh independent Blender check:

```text
blender --background --factory-startup --python-exit-code 17 --python tools/art013/verify_blends.py
```

The optional `--original-root` and `--deduplicate-packed` switches on that script
are one-time promotion operations. They are not needed to edit or verify this
checkout. Re-register deliberately edited masters and refresh source fingerprints
after review; do not silently accept changed inputs.
