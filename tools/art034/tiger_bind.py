"""Map exact official infantry bind matrices onto the cooked Tiger Hunter palette."""
from runtime import read_json, stock_game
from art016.repair import one, skins
from rig_contract import read_contract
from garrison_shared import relic_chunky as rc

def bind_tiger(root, asset, raw, baseline):
    source=read_json(root/'docs/update_014/OFFICIAL_RIG_CONTRACTS.json')[asset]['source']
    donor=stock_game.current().model_files(source,required=('.rgm',))['.rgm']
    assert one(donor,b'SKLN').payload==one(baseline,b'SKLN').payload
    assert read_contract(raw)['bones']==read_contract(donor)['bones']
    native=skins(one(donor,b'SKIN').payload)
    old=skins(one(raw,b'SKIN').payload)
    assert [(x['name'],x['parent']) for x in native]==[(x['name'],x['parent']) for x in old]
    bindings={tag:one(donor,tag).payload for tag in (b'SKLN',b'SKIN',b'SKEL')}
    result=rc.rebuild(rc.parse(raw),lambda c:bindings.get(c.tag))
    assert all(one(result,tag).payload==payload for tag,payload in bindings.items())
    return result
