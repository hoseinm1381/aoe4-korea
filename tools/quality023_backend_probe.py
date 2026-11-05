"""Silent installed-backend codec probe against the freshly built 0.2.3 archive."""
from pathlib import Path
import json
import voice022_backend_probe as probe
R=Path(__file__).resolve().parents[1]
receipt=json.loads((R/'docs/BUILD_VERIFICATION.json').read_text(encoding='utf-8'))
assert receipt['version']=='0.2.3'
probe.D=R/'docs/update_023'
probe.A=Path(receipt['assembly_path'])/'korea.sga'
if __name__=='__main__':probe.main()
