"""Read-only authoring environment check. Never downloads, cooks or installs."""
import sys
from pathlib import Path
if sys.version_info[:2]!=(3,13):raise SystemExit('Use Python 3.13 for this installed Garrison SDK ABI.')
from runtime import EXT,stock_game
for p in (EXT/'bin/core/garrison-core.exe',EXT/'bin/sga-archiver.exe'):
    if not p.is_file():raise SystemExit('Missing installed tool: '+str(p))
stock_game.current().blueprint('racebps/english')
print('Garrison SDK and installed game detected. Ready for local source edits.')
print('Verify inputs: python tools/inputs.py verify')
print('Build current candidate: python tools/build.py --replace-current')
