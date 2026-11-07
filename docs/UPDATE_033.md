# Korea 0.3.3 cavalry rebuild

The Horseman uses a compact dark riding cap, a short owner-colour saddlecloth, and light tack. The Knight uses a plated conical helmet, wider lamellar armor, and a longer barded flank. The Mounted Hwarang uses a Silla-inspired high crown, light robe panels, a pale horse and a gold-edged saddlecloth. The crown and horse trappings draw on the [National Museum of Korea's Silla mounted figures](https://www.museum.go.kr/ENG/contents/E0401000000.do?relicRecommendId=519710&schM=view). These are historically inspired game models.

Eight rider and horse pairs replace their existing private art across Horseman II–IV, Knight III–IV and Mounted Hwarang II–IV. The rebuild uses the current stock Chinese combined cavalry anatomy, weighted LODs and exact native animation binds. All 48 LOD meshes have revised geometry and shader atlases with dynamic owner-colour surfaces. Combat weapon and animation attachments use their existing owners. Building art, voices, SCAR, tuning and the civilization identity are byte-identical to 0.3.2.

## Editable source and rebuild

The 16 Blender masters and their albedo, normal, metalness and owner/skin mask PNGs are in `authoring/art033`. Each file has a stock rest-pose armature and three meshes with an explicit LOD number. Each palette uses the existing unit shader. The compiled equivalents in `inputs/native` let `BUILD.cmd --replace-current` assemble the full player ZIP without the original combined project.

`tools/art033/model.py` and `paint.py` record how the meshes and textures were authored from the five current stock combined cavalry references named in `docs/update_033/CAVALRY_MODELS.json`. For recooking, export the three edited meshes with the matching armature and material name, using the Garrison unit exporter with explicit triangulation. Stage those FBX and rig files and the four edited PNGs with `stage_cook.py`. Run the Garrison model-capable Content Editor through `garrison-core essence build-mod`, then match the stock SKIN indices and inverse binds before integrating. `compose.py` records the exact checks and integration used for this release. The compiled inputs and the editable input index both need updating after a recook.

## Verification

The command-line Content Editor model cook succeeded. Archive readback recovered all 48 LODs, matching source triangle counts and retaining the named stock weighted bones for each LOD. The SKIN palette order and hierarchy, inverse binds and SKLN owner blocks match the corresponding stock combined rigs. Package verification checks the complete member inventory, bytes, TOCs, archive identity and ZIP CRC.

Fresh Garrison import and in-game visuals remain to be verified. In a fresh Korea match, check near and distant movement, attack, charge and death for all three cavalry families, then switch Hwarang between foot and mounted forms. Test at least two player colours. Source/native asset readback does not exercise the game animation graph or qualify multiplayer and performance.

The editable Codex table was synchronized to the exact Codex bytes already shipped in 0.3.2 so a source rebuild reproduces the player ZIP. The original editable table remains in Git history.
