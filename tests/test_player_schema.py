"""Check the real scripts and player-data requirements against the owned schema."""
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def walk(nodes):
    for n in nodes:
        yield n
        if n['kind'] in ('List','List2'):yield from walk(n['value'])
class PlayerSchema(unittest.TestCase):
    def test_script_player_properties_have_native_definitions(self):
        cfg=json.loads((ROOT/'project.json').read_text())
        schema=ROOT/f"source/tables/attrib/statemodel_schema/garrison/{cfg['race']}/{cfg['race']}_player.rgd.json"
        ids={n['value'] for n in walk(json.loads(schema.read_text())['nodes'])
             if n['key'] and n['key'].endswith('_property_id')}
        for f in (ROOT/'source/scar').rglob('*.scar'):
            for name in re.findall(r'Player_(?:Get|Set)StateModel(?:Float|Bool|Int|Target)\s*\([^,]+,\s*["\']([^"\']+)["\']',f.read_text()):
                self.assertIn(name,ids,f'{f.relative_to(ROOT)} requires undefined player property {name}')
    def test_preserved_player_requirements_have_native_definitions(self):
        cfg=json.loads((ROOT/'project.json').read_text())
        review=json.loads((ROOT/'docs/PLAYER_SCHEMA_REVIEW.json').read_text())
        original=set(review['original_player_property_ids'])
        schema=ROOT/f"source/tables/attrib/statemodel_schema/garrison/{cfg['race']}/{cfg['race']}_player.rgd.json"
        ids={n['value'] for n in walk(json.loads(schema.read_text())['nodes'])
             if n['key'] and n['key'].endswith('_property_id')}
        for f in (ROOT/'source/tables').rglob('*.rgd.json'):
            for n in walk(json.loads(f.read_text())['nodes']):
                if n['kind'] not in ('List','List2'):continue
                fields={x['key']:x['value'] for x in n['value'] if x['kind'] not in ('List','List2')}
                if fields.get('data_source_type')=='player_datasource' and fields.get('key') in original:
                    self.assertIn(fields['key'],ids,f'{f.relative_to(ROOT)} requires undefined player property {fields["key"]}')
if __name__=='__main__':unittest.main()
