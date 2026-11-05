"""Insert removable diagnostic-only SCAR statements; preserve all original bytes."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'docs/update_024'
TAG=' -- KOREA024_DIAGNOSTIC'

def mark(indent,site,detail='nil',eol='\n'):
 return indent+'if KoreaDiag024_Mark then KoreaDiag024_Mark('+json.dumps(site)+','+detail+') end'+TAG+eol

def main():
 specs={
 'core.scar':[
 ('local full = KoreaCatalog[category]','bp.cache_miss','key','before'),
 ('local modifier = Modifier_Create','modifier.create','property','both'),
 ('local handle = Modifier_ApplyTo','modifier.apply','property','both'),
 ('Modifier_Remove(handle)','modifier.remove','nil','both'),
 ('Player_GetEntitiesEGroup(player.id, group)','entities.snapshot','nil','both'),
 ('local entity = EGroup_GetEntityAt(group, i)','entities.chunk','i','before_chunk'),
 ('local squad = SGroup_GetSpawnedSquadAt(group, i)','squads.chunk','i','before_chunk'),
 ('local entity = Squad_GetFirstEntity(squad)','squads.first_entity','i','before_chunk')],
 'effects.scar':[
 ('Entity_ConvertBlueprint(entity, ebp)','transform.entity_convert','target','both'),
 ('Squad_ConvertBlueprint(squad, sbp)','transform.squad_convert','target','both'),
 ('Entity_SetHealth(entity, health)','transform.set_health','health','both'),
 ('local previous = KoreaState.debuffs[id]','damage.spear_debuff','id','before'),
 ('local handle = Modifier_ApplyToEntity','barrage.modifier_apply','nil','both'),
 ('LocalCommand_EntityPos(','barrage.entity_attack','nil','both'),
 ('LocalCommand_SquadPos(','barrage.squad_attack','nil','both'),
 ('LocalCommand_Entity(record.player.id','barrage.entity_stop','record.id','both'),
 ('LocalCommand_Squad(record.player.id','barrage.squad_stop','record.id','both'),
 ('Player_CompleteUpgrade(','upgrade.automatic_followup','nil','both'),
 ('local entity = Korea_Entity(id)','barrage.resolve_entity','id','both')],
 'economy.scar':[
 ('World_GetNeutralEntitiesNearPoint(','seowon.neutral_scan','id','both'),
 ('Entity_QueueProductionItemByPBG(','seowon.queue_reward','id','both'),
 ('player.nextAcademy = now + 15','economy.academy_income','now','before'),
 ('player.nextHangul = now + 6','economy.hangul_income','now','before'),
 ('player.nextWater = now + 30','economy.water_income','now','before'),
 ('local entity = Korea_Entity(academy.id)','economy.resolve_academy','academy.id','both'),
 ('Entity_SetStateModelFloat(entity,','economy.state_write','academy.id','both'),
 ('local supervised = Entity_GetStateModelBool','economy.supervision_read','id','both')],
 'landmarks.scar':[
 ('local squad = Squad_CreateAndSpawnToward','guards.spawn','nil','both'),
 ('Misc_SetSquadSelectable(','guards.selectability','nil','both'),
 ('if Entity_QueueProductionItemByPBG(','landmark.queue_reward','nil','before'),
 ('World_GetSquadsNearPoint(','guards.enemies','nil','both'),
 ('World_GetEntitiesNearPoint(','guards.buildings','nil','both'),
 ('Cmd_AttackMove(','guards.attack_move','nil','both'),
 ('Cmd_Move(','guards.patrol_move','nil','both'),
 ('if World_DistancePointToPoint(Entity_GetPosition(palace)','palace.dead_victim_position','nil','before')],
 'research.scar':[
 ('local route = KoreaResearchRoutes[key(context.ability)]','research.ability_route','nil','both'),
 ('if not Entity_QueueProductionItemByPBG(','research.queue_upgrade','route.upgrade','before'),
 ('local costs, transaction = KoreaResearchCore.Settle','research.settlement','upgrade','both')],
 'ui.scar':[
 ('UI_SetDataContext(','ui.publish','KoreaUI.visible','both'),
 ('local info = BP_GetUpgradeUIInfo','ui.upgrade_info','name','both')],
 'voices_020.scar':[
 ('audio.pulse(now)','voice.pulse','nil','both'),
 ('Misc_GetSelectedSquads(','voice.selection','nil','both'),
 ('Rule_AddSquadEvent(','voice.register_callback','id','both'),
 ('Rule_RemoveSquadEvent(','voice.remove_callback','r.id','both'),
 ('if not audio.play(','voice.submit','clip[1]','before'),
 ('S.sent=(S.sent or 0)+1','voice.submit_succeeded','clip[1]','before'),
 ('if now>=S.nextScan then','voice.roster','nil','before'),
 ('for id,r in pairs(S.actors) do','voice.reactions','nil','before'),
 ('local current=activity(r.squad)','voice.activity','id','both')]
 }
 ledger=[]
 for filename,rules in specs.items():
  p=R/'source/scar/korea'/filename;raw=p.read_bytes()
  # Resume an interrupted diagnostic pass from exactly the same baseline bytes.
  raw=b''.join(s for s in raw.splitlines(keepends=True) if TAG.encode() not in s)
  assert hashlib.sha256(raw).hexdigest()==json.loads((D/'baseline-source.json').read_text())[p.relative_to(R).as_posix()]
  lines=raw.decode('utf-8').splitlines(keepends=True);out=[];hits=[0]*len(rules)
  for line in lines:
   stripped=line.lstrip();indent=line[:len(line)-len(stripped)];eol='\r\n' if line.endswith('\r\n') else '\n'
   found=[]
   for k,(pattern,site,detail,when) in enumerate(rules):
    if pattern in line and not stripped.startswith('--'):
     hits[k]+=1;found.append((site,detail,when))
     text=mark(indent,site+'.before',detail,eol)
     if when=='before_chunk':text=indent+'if i%32==1 and KoreaDiag024_Mark then KoreaDiag024_Mark('+json.dumps(site)+',i) end'+TAG+eol
     out.append(text)
   out.append(line)
   for site,detail,when in found:
    if when=='both':out.append(mark(indent,site+'.after',detail,eol))
  assert all(hits),(filename,hits)
  updated=''.join(out).encode();restored=b''.join(s for s in updated.splitlines(keepends=True) if TAG.encode() not in s)
  assert restored==raw,filename
  p.write_bytes(updated);ledger.append({'file':p.relative_to(R).as_posix(),'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(updated).hexdigest(),'sites':[{'pattern':rule[0],'label':rule[1],'hits':n} for rule,n in zip(rules,hits)],'exact_original_bytes_after_removing_diagnostic_lines':True})
 p=R/'source/scar/garrison/korea/dispatcher.scar';raw=p.read_bytes();eol='\r\n' if b'\r\n' in raw else '\n';line='import("korea/diagnostics_024.scar")'+TAG+eol;needle=('import("korea/voices_020.scar")'+eol).encode()
 assert needle in raw
 p.write_bytes(raw.replace(needle,needle+line.encode(),1));ledger.append({'file':p.relative_to(R).as_posix(),'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'exact_original_bytes_after_removing_diagnostic_lines':True})
 (D/'INSTRUMENTATION.json').write_text(json.dumps(ledger,indent=2)+'\n')
 print('INSTRUMENTED',len(ledger),'files; all original statements/order/bytes recover exactly')
if __name__=='__main__':main()
