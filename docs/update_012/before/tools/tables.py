"""Find, inspect and edit native scalar fields without touching opaque metadata.

python tools/tables.py find villager
python tools/tables.py show <table.rgd.json> health_max
python tools/tables.py set <table.rgd.json> <exact/printed/path> <JSON-value>
"""
import argparse,json
from runtime import ROOT,read_json,write_json,import_table,rgd
def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    f=sub.add_parser('find');f.add_argument('text')
    for name in ('show','set'):
        s=sub.add_parser(name);s.add_argument('table');s.add_argument('field',nargs='?' if name=='show' else None,default='')
        if name=='set':s.add_argument('value')
    a=p.parse_args()
    if a.action=='find':
        for f in (ROOT/'source/tables').rglob('*.rgd.json'):
            if a.text.lower() in f.as_posix().lower():print(f.relative_to(ROOT).as_posix())
        return
    f=(ROOT/a.table).resolve()
    if not f.is_relative_to((ROOT/'source/tables').resolve()):raise ValueError('Expected source/tables path')
    data=read_json(f);doc=rgd.read(import_table(data));matches=[]
    for path,node in rgd.flatten(doc.nodes):
        if not isinstance(node.value,list) and a.field in path:
            matches.append((path,node))
            if a.action=='show':print(path,node.kind,json.dumps(node.value,ensure_ascii=False))
    if a.action=='show':return
    exact=[n for path,n in matches if path==a.field]
    if len(exact)!=1:raise ValueError('Use one exact printed scalar path')
    value=json.loads(a.value);target=exact[0]
    if target.kind=='Boolean' and type(value) is not bool:raise ValueError('Expected JSON boolean')
    if target.kind in ('CString','String','LocString') and not isinstance(value,str):raise ValueError('Expected JSON string')
    if target.kind=='Int' and type(value) is not int:raise ValueError('Expected integer')
    if target.kind=='Float' and type(value) not in (int,float):raise ValueError('Expected numeric value')
    def update(nodes):
        for n in nodes:
            if n['kind'] in ('List','List2'):update(n['value'])
    # Native flatten ordering is retained exactly in the serialized source.
    flat=[]
    def leaves(nodes):
        for n in nodes:
            if n['kind'] in ('List','List2'):leaves(n['value'])
            else:flat.append(n)
    leaves(data['nodes'])
    live=[n for _,n in rgd.flatten(doc.nodes) if not isinstance(n.value,list)]
    flat[live.index(target)]['value']=value
    import_table(data) # Validate native types/keys before replacing source.
    write_json(f,data);print('UPDATED',f,a.field)
if __name__=='__main__':main()

