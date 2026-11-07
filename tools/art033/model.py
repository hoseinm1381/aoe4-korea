"""Create the eight age-specific rider/horse pairs on exact stock combined rigs."""
import inspect
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Matrix

STAGE = Path(os.environ['KOREA_ART033_STAGE'])
EXT = Path(os.environ['APPDATA']) / 'Blender Foundation/Blender/5.2/extensions/raw_githubusercontent_com/garrison'
sys.path[:0] = [str(EXT), str(EXT.parent)]
from garrison_shared import unit_model_export as native
import garrison
sys.modules['garrison.garrison_shared'] = sys.modules['garrison_shared']
garrison.register()
from garrison import unit_export
from garrison.unit_animation import BONE_AXES, COOKED_TO_BLENDER
from mathutils import Quaternion, Vector
from mathutils.bvhtree import BVHTree

code = inspect.getsource(unit_export.export_unit_model)
assert code.count('filepath=str(output),') == 1
exporter = dict(vars(unit_export))
exec(compile(code.replace('filepath=str(output),', 'filepath=str(output), use_triangles=True,'),
             'triangulated-cavalry-export', 'exec'), exporter)


def create_rig(records):
    bones = bpy.data.armatures.new('Native cavalry rest skeleton')
    rig = bpy.data.objects.new('CavalryRig', bones)
    bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for record in records:
        bone = bones.edit_bones.new(record['name'])
        if record['parent_name']:
            bone.parent = bones.edit_bones[record['parent_name']]
        rest = record['global_reference_transform']
        x, y, z, w = rest['quaternion_xyzw']
        transform = Matrix.LocRotScale(Vector(rest['translation_xyz']), Quaternion((w,x,y,z)), Vector(rest['scale_xyz']))
        bone.head = (0,0,0)
        bone.tail = (0,.08,0)
        bone.matrix = Matrix(COOKED_TO_BLENDER) @ transform @ Matrix(BONE_AXES)
        bone.length = .08
    bpy.ops.object.mode_set(mode='OBJECT')
    rig[native.RIG_RECORDS_KEY] = json.dumps(records)
    return rig


def tile_uv(tile, u=.5, v=.5):
    return (.764 + .220 * u, 1 - (tile + .12 + .76 * v) / 8)


class Surface:
    def __init__(self):
        self.vertices = []
        self.weights = []
        self.faces = []
        self.uv = []

    def add(self, point, weights):
        index = len(self.vertices)
        self.vertices.append(point)
        self.weights.append(weights)
        return index

    def face(self, indices, uv):
        self.faces.append(tuple(indices))
        self.uv.append(tuple(uv))

    def rings(self, center, rings, sides, bone):
        cx, cy, cz = center
        loops = []
        for dx, dy, z, rx, ry, tile in rings:
            loop = []
            for i in range(sides):
                a = math.tau * i / sides
                loop.append(self.add((cx + dx + rx*math.cos(a), cy + dy + ry*math.sin(a), cz + z), {bone: 1.0}))
            loops.append(loop)
        for index, (a, b) in enumerate(zip(loops, loops[1:])):
            tile = rings[index+1][-1]
            for j in range(sides):
                k = (j+1)%sides
                p, q, r, s = [tile_uv(tile,u,v) for u,v in ((0,0),(1,0),(1,1),(0,1))]
                self.face((a[j],a[k],b[k]), (p,q,r))
                self.face((a[j],b[k],b[j]), (p,r,s))
        for loop, direction in ((loops[0], -1), (loops[-1], 1)):
            seq = loop[::direction]
            for j in range(1,len(seq)-1):
                self.face((seq[0],seq[j],seq[j+1]), (tile_uv(rings[-1][-1]),)*3)


def add_saddle_panels(surface, family, lod, age):
    # Project the cloth and lamellar skirts onto the skinned flank. The panel
    # rides with the exact same deform bones as its supporting horse surface.
    y_range = {'horseman': (-.23, .46), 'lancer': (-.46, .66), 'hwarang': (-.27, .63)}
    bottom = {'horseman': 1.31, 'lancer': 1.14, 'hwarang': 1.23}[family] - .015 * (age-2)
    y_min, y_max = y_range[family]
    trees = BVHTree.FromPolygons(surface.vertices, surface.faces, all_triangles=True)
    base_faces = list(surface.faces)
    cols = (6, 4, 3)[lod-1]
    for side in (-1,1):
        points = []
        for row in range(3):
            level = (1.54, bottom + .055, bottom)[row]
            for col in range(cols+1):
                t = col / cols
                y = y_min + t * (y_max-y_min)
                z = level
                if row and family == 'hwarang':
                    z += .09 * abs(2*t-1)
                hit, _, index, _ = trees.ray_cast(Vector((side*.9,y,z)), Vector((-side,0,0)), .9)
                if hit is None:
                    # A tapered hem ends at the last supported surface.
                    hit, _, index, distance = trees.find_nearest(Vector((side*.29,y,z)))
                    assert distance < .30, (family, lod, y,z,distance)
                nearest = min(base_faces[index], key=lambda i: (Vector(surface.vertices[i])-hit).length_squared)
                hit.x += side * (.021 + row*.008)
                points.append(surface.add(tuple(hit), surface.weights[nearest]))
        for row in range(2):
            tile = 1 if row == 1 else {'horseman': 2, 'lancer': 6, 'hwarang': 5}[family]
            for col in range(cols):
                i = row*(cols+1)+col
                a,b,c,d = [points[j] for j in (i,i+1,i+cols+2,i+cols+1)]
                uv = [tile_uv(tile,u,v) for u,v in ((col/cols,0),((col+1)/cols,0),((col+1)/cols,1),(col/cols,1))]
                for corners in ((0,1,2),(0,2,3)):
                    if side < 0:
                        corners = corners[::-1]
                    surface.face([(a,b,c,d)[k] for k in corners], [uv[k] for k in corners])


def build_surface(doc, spec, lod):
    part, family, age = (spec[k] for k in ('part','family','age'))
    out = Surface()
    palettes = doc['skeleton']['skin_palettes']
    group_list = [g for g in doc['geometry']['groups'] if g['material'] == f'{part}_lod{lod}']
    assert group_list, (spec['asset'],lod)
    for group in group_list:
        palette = {p['palette_index']: p['name'] for p in palettes[group['rig_projection']['palette_index']]['bones']}
        uvs = next(iter(group['uv_layers'].values()))
        indices = []
        for (x, y, z), slots, weights in zip(group['positions'], group['skin_indices'], group['skin_weights'], strict=True):
            binding = {}
            for slot, weight in zip(slots, weights, strict=True):
                if weight > 0:
                    bone = palette[slot]
                    binding[bone] = binding.get(bone, 0) + weight
            assert binding
            total = sum(binding.values())
            binding = {bone: w / total for bone,w in binding.items()}
            if part == 'rider':
                if z > 1.81:
                    z = 1.81 + min(z-1.81,.24) * .34
                if abs(x) < .27 and .95 < z < 1.57:
                    x *= {'horseman': .95, 'lancer': 1.14, 'hwarang': 1.0}[family]
            elif .73 < z < 1.70:
                x *= {'horseman': .95, 'lancer': 1.07, 'hwarang': 1.0}[family]
            indices.append(out.add((x,y,z), binding))
        for tri in group['triangles']:
            xyz = [out.vertices[indices[i]] for i in tri]
            x,y,z = (sum(p[i] for p in xyz)/3 for i in range(3))
            tile = None
            if part == 'rider':
                if .99 < z < 1.53 and abs(x) < .29:
                    tile = {'horseman': 2 if abs(y)>.09 else 7,
                            'lancer': 6 if z>1.17 else 5,
                            'hwarang': 3 if z>1.13 else 5}[family]
                elif z > 1.87:
                    tile = 0 if family != 'lancer' else 6
                uv = [tile_uv(tile, max(0,min(1,(p[0]+.3)/.6)), max(0,min(1,(p[2]-1.0)/.52))) for p in xyz] if tile is not None else None
            else:
                uv = None
            out.face([indices[i] for i in tri], uv or [(uvs[i][0]*.75, uvs[i][1]) for i in tri])
    if part == 'rider':
        # Sculpted helmet and lower band overlap the original scalp, whose donor
        # bind remains exact. The crown shape remains visible in the distant LOD.
        sides = (12, 8, 6)[lod-1]
        head = 'metarig_head'
        if family == 'horseman':
            rings = [(0,0,0,.157,.141,0),(0,0,.025,.166,.149,2),(0,.007,.063,.122,.124,0),(0,.014,.148,.045,.046,0)]
        elif family == 'lancer':
            rings = [(0,0,0,.156,.142,6),(0,0,.035,.174,.154,1),(0,0,.105,.141,.130,6),(0,.005,.194,.079,.079,6),(0,.01,.224+age*.009,.031,.032,1)]
        else:
            rings = [(0,0,0,.147,.140,0),(0,0,.032,.152,.144,1),(0,.014,.10,.124,.117,0),(0,.021,.215,.060,.065,0),(0,.036,.258,.042,.041,5),(0,.079,.331+age*.014,.014,.022,1)]
        out.rings((0, .022, 1.788), rings, sides, head)
    else:
        add_saddle_panels(out, family, lod, age)
    return out


def make_mesh(surface, rig, material, name, lod):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(surface.vertices, [], surface.faces)
    mesh.validate(verbose=False)
    assert len(mesh.polygons) == len(surface.faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(material)
    uv_layer = mesh.uv_layers.new(name='UVMap')
    for poly, uv in zip(mesh.polygons, surface.uv, strict=True):
        poly.use_smooth = True
        for i, point in zip(poly.loop_indices, uv, strict=True):
            uv_layer.data[i].uv = point
    groups = {n: obj.vertex_groups.new(name=n) for n in sorted(set().union(*surface.weights))}
    for i, weights in enumerate(surface.weights):
        for n,w in weights.items():
            groups[n].add([i],w,'REPLACE')
    obj.modifiers.new('Native skin', 'ARMATURE').object = rig
    obj['lod'] = lod
    return obj


def run(spec):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    doc = json.loads(Path(spec['manifest']).read_text())
    records = doc['skeleton']['bones']
    assert len(records) == 127 and not doc['blockers']
    asset = spec['asset']
    folder = STAGE / 'authoring' / asset
    rig = create_rig(records)
    material = bpy.data.materials.new(asset + '_atlas')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    for role in ('albedo', 'normal', 'metalness', 'pattern'):
        texture = nodes.new('ShaderNodeTexImage')
        texture.label = role
        texture.image = bpy.data.images.load(str(folder / (role + '.png')))
        texture.image.filepath = '//' + role + '.png'
        if role != 'albedo':
            texture.image.colorspace_settings.name = 'Non-Color'
        else:
            material.node_tree.links.new(texture.outputs['Color'], nodes.get('Principled BSDF').inputs['Base Color'])
    lods = [make_mesh(build_surface(doc,spec,n), rig, material, asset+f'_lod{n}',n) for n in (1,2,3)]
    for obj in lods[1:]:
        obj.hide_set(True)
        obj.hide_render = True
    rig.hide_set(True)
    bpy.context.view_layer.objects.active = lods[0]
    lods[0].select_set(True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/(asset+'.blend')),relative_remap=False)
    rig.hide_set(False)
    destination = STAGE / 'exports' / asset
    destination.mkdir(parents=True, exist_ok=True)
    n = len(records)
    exporter['export_unit_model'](rig,lods[:1],destination/'model.fbx',records,
                                  three_lods=True,lod_counts=(n,n,n),lod_meshes={2:lods[1],3:lods[2]})
    native.write_rig(destination,native.rig_text(records,partitions=[('FullBody_LOD3',0,n)]))
    print('CAVALRY_EXPORT',asset,[len(o.data.polygons) for o in lods],flush=True)


for spec in json.loads((STAGE/'assets.json').read_text()):
    if not os.environ.get('KOREA_ART033_PILOT') or spec['asset'] in {'kr_horseman_a2','kr_mount_horseman_a2'}:
        run(spec)
