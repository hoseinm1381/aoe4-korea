"""Real-source regression for engineer construction and both Codex surfaces."""
import sys,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from runtime import read_json,import_table,rgd,at,child
from codex import build
class ConstructionCodex(unittest.TestCase):
    def test_owned_engineer_squads_and_both_native_views(self):
        config=read_json(ROOT/'project.json');tables={p.relative_to(ROOT/'source/tables').as_posix()[:-5]:rgd.read(import_table(read_json(p))) for p in (ROOT/'source/tables').rglob('*.rgd.json')}
        doc,report=build(tables,config)
        self.assertGreater(report['producer_count'],15)
        self.assertGreaterEqual(sum('landmark' in x['producer'] for x in report['groups']),6)
        views=[]
        for variant in ('default','campaign'):
            bag=at(doc,variant+'/codex_bag');groups=child(bag,'tech_tree').value
            headers={child(child(child(g,'items').value[0],'pbg'),'$PBGNAME').value for g in groups}
            roots={child(child(n,'pbg'),'$PBGNAME').value for n in child(child(bag,'root_item'),'children').value}
            self.assertEqual(headers,roots);views.append(headers)
        self.assertEqual(views[0],views[1])
    def test_accepted_starting_resources_and_allowances(self):
        config=read_json(ROOT/'project.json');path=next((ROOT/'source/tables/attrib/army').rglob('*.rgd.json'));doc=rgd.read(import_table(read_json(path)))
        expected={'vietnam':{'food':150,'wood':200,'gold':100,'stone':0,'action':0},'persia':{'food':200,'wood':200,'gold':100,'stone':0,'action':0},'korea':{'food':150,'wood':200,'gold':50,'stone':0,'action':2}}[config['race']]
        resources={n.key:n.value for n in at(doc,'default/army_bag/resource_starting_amount').value}
        for key,value in expected.items():self.assertEqual(resources[key],value,key)
        if config['race']=='korea':self.assertEqual(at(doc,'default/army_bag/resource_max_cap/merc_byz').value,100000)
if __name__=='__main__':unittest.main()
