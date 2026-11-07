# Korea 0.3.1

Nine unique buildings use their original owner-colour atlas with paired accents on timber and masonry surfaces. The healthy LOD0 meshes project about 0.6–2.9% additional owner-mask coverage from the new bands. Repeated UV islands can repeat an accent. Palace and Mountain Fortress geometry and footprints retain their 0.3.0 dimensions.

Gyeongbok Palace omits the native scuttle ability and hides its Delete command. Enemy destruction and native repair remain available. The barrage controller invalidates an interrupted Palace barrage, releases the timed modifiers, and checks the old forced attack when the repaired entity is active again. It sends no command to a ruin. This addresses a script lifetime gap. The original native crash signature was unavailable.

The six Korean landmarks now include 29 native visual state transitions from the current stock Forbidden Palace object. In 0.3.0 the Korean RGO controllers had the state names but empty behaviour and action folders. The replacement rules drive the existing Korean construction, damage, ruins and healthy meshes from the stock build, health and preview inputs. The package retains each landmark's own meshes, stamp, collision and functional objects.

## Acceptance

- Blender source audit projected the narrow stripes onto the nine healthy LOD0 meshes. Native texture encoding and BC3 readback validated 12 mip levels.
- Two edited SCAR modules passed static validation with one inherited PLAYERS warning. The MCP checker identified local Lua symbols and an existing documented cost call. Seven focused Lua scenarios passed against a stubbed engine.
- The editable and compiled Palace scuttle fields are kept in sync. The current Garrison assembly validates the typed native tables and reads back the full archive.
- For a fresh Korea match, verify the missing Palace Delete button, fire the barrage at empty ground, let an enemy destroy the Palace during the barrage, then repair it fully. The Korean model should return without a resumed barrage. Cast again to check that fresh barrages work. Repeat repair on a second Korean landmark and check two player colours from normal game zoom.
- In-game appearance, repair timing, and crash recurrence need fresh match validation.
