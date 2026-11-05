"""Apply the four admitted 0.2.1 source repairs after baseline preparation."""
from pathlib import Path
import gzip
R=Path(__file__).resolve().parents[1];D=R/'docs/update_021'
assert (D/'BANK_ROUTING.json').exists()
p=R/'source/scar/korea/voices_020.scar';s=p.read_text(encoding='utf-8')
needle='local audio=Garrison.audio.forMod("korea")\n'
assert s.count(needle)==1
s=s.replace(needle,needle+'''
-- Match exact compiled PBG IDs first, as the working Berber adapter does.
-- Admit an unqualified name only through this mod's known owner namespace.
local function voiceConfig(bp)
    if not bp then return nil end
    local mapped=bank.pbgids and bank.pbgids[bp.PropertyBagGroupID]
    if mapped then return mapped end
    local name=string.lower(BP_GetName(bp))
    local owner="748d61b94d3e4cf3a506a9ac1f992d1d:"
    if not string.find(name,":",1,true) then name=owner..name end
    return bank.units[name]
end
''')
s=s.replace('local config=bp and bank.units[string.lower(BP_GetName(bp))]','local config=voiceConfig(bp)')
s=s.replace('    if not audio.play(clip[1],x,z,gain) then return false end','''    if not audio.play(clip[1],x,z,gain) then
        S.sendFailures=(S.sendFailures or 0)+1
        if S.sendFailures<=3 then print("KOREA_VOICE_SEND_FAILED key=korea") end
        return false
    end
    S.sent=(S.sent or 0)+1
    -- Submission is not a backend playback acknowledgement.
    if S.sent<=20 then print("KOREA_VOICE_QUEUED role="..r.role.." age="..tostring(r.age).." event="..event) end''')
needle='    local age=config.age or playerAge(entry.id)'
assert needle in s
s=s.replace(needle,'''    if not S.loggedRoles[role] then
        S.loggedRoles[role]=true
        print("KOREA_VOICE_BOUND role="..role.." blueprint="..BP_GetName(bp).." pbgid="..tostring(bp.PropertyBagGroupID))
    end
'''+needle)
s=s.replace('    audio.session()\n','    S.sent=0;S.sendFailures=0;S.loggedRoles={}\n    audio.session()\n    print("KOREA_VOICE_STARTED key=korea; queued cues require the normal Garrison audio backend")\n')
p.write_text(s,encoding='utf-8')
p=R/'source/scar/garrison/korea/dispatcher.scar';s=p.read_text(encoding='utf-8')
needle='local state=KoreaIndependentState\n'
s=s.replace(needle,needle+'''local function startLocalVoices()
    if not KoreaVoice_Start then return end
    local player=Game_GetLocalPlayer()
    if next(state.civilizations)~=nil or (player~=nil and Player_GetRaceName(player)=="748d61b94d3e4cf3a506a9ac1f992d1d:korea") then
        KoreaVoice_Start(state.civilizations)
    end
end
''')
s=s.replace('    if next(state.civilizations)==nil then return end','    -- Voice presentation follows the selected local race, independently of the gameplay start guard.\n    startLocalVoices()\n    if next(state.civilizations)==nil then return end')
s=s.replace('    if KoreaVoice_Start then KoreaVoice_Start(state.civilizations) end\n','')
s=s.replace('    if not state.active then return end\n    -- Retained restore hooks','    if not state.started or state.ending then return end\n    -- Retained restore hooks')
s=s.replace('    if KoreaVoice_Stop then KoreaVoice_Stop() end\nend\nfunction KoreaIndependent_OnGameOver','    if KoreaVoice_Stop then KoreaVoice_Stop() end\n    startLocalVoices()\nend\nfunction KoreaIndependent_OnGameOver')
p.write_text(s,encoding='utf-8')
p=R/'tools/build.py';s=p.read_text(encoding='utf-8')
(D/'build.py.before-021.gz').write_bytes(gzip.compress(p.read_bytes(),mtime=0))
needle="    if config['version']=='0.2.0':\n        from voice020_release import verify_source as verify_voice020_source"
assert needle in s
s=s.replace(needle,"    if config['version']=='0.2.1':\n        from release021 import verify as verify021\n        verify021()\n    elif config['version']=='0.2.0':\n        from voice020_release import verify_source as verify_voice020_source")
s=s.replace("\n    if config['version']=='0.2.0':\n","\n    if config['version'] in ('0.2.0','0.2.1'):\n")
s=s.replace("'2026-11-02' if config['version']=='0.2.0' else","'2026-11-02' if config['version'] in ('0.2.0','0.2.1') else")
needle="    delivery=out/'delivery';package="
assert needle in s
s=s.replace(needle,"    if config['version']=='0.2.1':details.update(min_garrison='0.1.13',changelog='0.2.1: restore five native starting sheep; match Korean voices by compiled PBG ID and known owner names like Berber; initialize local voice presentation independently of gameplay enrollment. Original audio, models, research and identity preserved. A successful normal Garrison launch is required for its audio backend.')\n"+needle)
needle="    write_json(out/'verification.json',receipt)"
s=s.replace(needle,"    if config['version']=='0.2.1':receipt.update(zip_increment_vs_020=package.stat().st_size-read_json(ROOT/'docs/update_021/baseline-build.json')['zip_bytes'],native_starting_sheep=5,normal_client_audio_launch_required=True)\n"+needle)
compile(s,str(p),'exec');p.write_text(s,encoding='utf-8')
print('Applied scoped voice routing/start diagnostics and current-SDK 0.2.1 build metadata.')
