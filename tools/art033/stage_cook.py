"""Stage the skinned visual FBXs for a CLI-only Garrison model cook."""
from pathlib import Path
import json
import shutil
import sys
import xml.etree.ElementTree as ET

repo, stage, label = map(Path, sys.argv[1:4])
project = stage / label
template = repo / 'source/art013/cook-template'
shutil.copytree(template, project)
for spec in json.loads((stage/'assets.json').read_text()):
    asset = spec['asset']
    export = stage/'exports'/asset
    if not export.is_dir():
        continue
    stem = 'art/kr013/units/' + asset
    target = project/'source'/stem
    target.mkdir(parents=True)
    for name in ('model.fbx', 'model.rig'):
        shutil.copy2(export/name, target/name)
    for name in ('model.rgo', 'model.rgotemplate'):
        shutil.copy2(template/name, target/name)
    materials = ET.Element('materialSet')
    material = ET.SubElement(materials, 'material', name=asset+'_atlas', type='shader', source='unit')
    for role, slot in [('albedo','albedoTexture'),('pattern','patternTex'),('normal','normalMap'),('metalness','metalTex')]:
        name = role + '.png'
        shutil.copy2(stage/'authoring'/asset/name, target/name)
        ET.SubElement(material, 'param', name=slot, type='tex2D', value=stem+'/'+name)
    ET.ElementTree(materials).write(target/'model.material', encoding='utf-8', xml_declaration=True)
