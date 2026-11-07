"""Author the three Tiger Hunter tiers from the existing Korean rigged masters."""
import inspect
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT, STAGE = map(Path,sys.argv[-2:])
EXT = Path(os.environ['APPDATA']) / 'Blender Foundation/Blender/5.2/extensions/raw_githubusercontent_com/garrison'
sys.path[:0] = [str(EXT), str(EXT.parent), str(STAGE)]
from garrison_shared import unit_model_export as native
import garrison
sys.modules['garrison.garrison_shared'] = sys.modules['garrison_shared']
garrison.register()
from garrison import unit_export
code = inspect.getsource(unit_export.export_unit_model)
assert code.count('filepath=str(output),') == 1
exporter = dict(vars(unit_export))
exec(compile(code.replace('filepath=str(output),', 'filepath=str(output), use_triangles=True,'),
             'triangulated-tiger-hunter-export', 'exec'), exporter)

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


def saturate(value):
    return max(0, min(1, value))


def source_surface(obj, age, lod):
    out = Surface()
    group_names = [g.name for g in obj.vertex_groups]
    for vertex in obj.data.vertices:
        x,y,z = vertex.co
        binding = {group_names[g.group]: g.weight for g in vertex.groups if g.weight > 0}
        assert binding
        # Taper the old cap under the newly modeled helmet.
        if z > 1.81:
            z = 1.81 + (z-1.81)*.34
        out.add((x,y,z), binding)
    obj.data.calc_loop_triangles()
    uv_layer = obj.data.uv_layers.active.data
    for tri in obj.data.loop_triangles:
        points = [out.vertices[i] for i in tri.vertices]
        x,y,z = (sum(p[i] for p in points)/3 for i in range(3))
        tile = None
        if 1.06 < z < 1.51 and abs(x) < .242:
            tile = 6 if age == 4 else 4 if age == 3 else 3
        elif .73 < z < 1.06 and abs(x) < .28:
            tile = 5 if abs(x) > .10 and age > 2 else 2
        elif 1.58 < z < 1.68 and abs(x) < .18 and y > -.08:
            tile = 5
        uv = ([tile_uv(tile,saturate((q[0]+.28)/.56),saturate((q[2]-.75)/.76)) for q in points]
              if tile is not None else [(uv_layer[i].uv[0]*.75,uv_layer[i].uv[1]) for i in tri.loops])
        out.face(tri.vertices, uv)

    hull = BVHTree.FromPolygons(out.vertices,out.faces,all_triangles=True)
    original = list(out.faces)

    def fitted(side, x, z, offset):
        location, _, index, _ = hull.ray_cast(Vector((x,side*.48,z)),Vector((0,-side,0)),.48)
        assert location is not None,(age,lod,x,z,side)
        a,b,c = original[index]
        v,w,u = [Vector(out.vertices[i]) for i in (a,b,c)]
        va, vb, hit = w-v,u-v,location-v
        aa,ab,bb = va.dot(va),va.dot(vb),vb.dot(vb)
        denominator = aa*bb-ab*ab
        beta = (bb*va.dot(hit)-ab*vb.dot(hit))/denominator
        gamma = (aa*vb.dot(hit)-ab*va.dot(hit))/denominator
        weights = {}
        for i,mix in zip((a,b,c),(1-beta-gamma,beta,gamma),strict=True):
            for bone,value in out.weights[i].items():
                weights[bone] = weights.get(bone,0)+max(0,mix)*value
        kept = sorted(weights.items(),key=lambda x:-x[1])[:4]
        total = sum(v for _,v in kept)
        location.y += side*offset
        return out.add(tuple(location),{k:v/total for k,v in kept if v>0.00001})

    def plate(side, corners, tile, offset=.024):
        ids=[fitted(side,x,z,offset) for x,z in corners]
        uv=[tile_uv(tile,u,v) for u,v in ((0,1),(1,1),(1,0),(0,0))]
        for seq in ((0,1,2),(0,2,3)):
            if side < 0:
                seq = seq[::-1]
            out.face([ids[i] for i in seq],[uv[i] for i in seq])

    # Overlapping fitted rows and end stitching read at the default camera.
    rows = (2,3,4)[age-2]
    columns = (6,4,3)[lod-1]
    if lod == 3:
        rows -= 1
    for side in (-1,1):
        for row in range(rows):
            z = 1.435-row*.093
            span = (.184 + row*.008) * (1 if age > 2 else .92)
            for col in range(columns):
                x = -span + col*(2*span/columns)
                width=2*span/columns-.004
                plate(side,[(x,z),(x+width,z),(x+width-.007,z-.088),(x+.005,z-.088)],
                      3 if age==2 else 4 if age==3 else 6,.022+row*.005)
        # Wide cloth-and-metal waist tie, with dynamic owner tint.
        plate(side,[(-.172,1.125),(.172,1.125),(.170,1.077),(-.170,1.077)],2,.051)
        plate(side,[(-.054,1.125),(.054,1.125),(.05,1.077),(-.05,1.077)],1,.054)

    sides=(12,8,6)[lod-1]
    rings=[(0,0,0,.147,.142,0),(0,0,.024,.164,.153,1),
           (0,.012,.075,.145,.139,0),(0,.020,.130+.015*(age-2),.101,.100,0),
           (0,.024,.158+.035*(age-2),.045,.053,6 if age>2 else 0)]
    if age == 4:
        rings += [(0,.026,.24,.033,.034,1),(0,.030,.276,.015,.015,1)]
    out.rings((0,.026,1.794),rings,sides,'metarig_head')
    if age >= 3:
        # Three-sided fabric/iron neck guard. It leaves the face and drawing arm open.
        guard_points=[]
        for level,radius in ((1.80,.141),(1.65,.159 if age==4 else .149)):
            for i in range(sides+1):
                angle=-.13+i*(math.pi+.26)/sides
                guard_points.append(out.add((radius*math.cos(angle),.028+radius*.89*math.sin(angle),level),{'metarig_head':1.0}))
        for i in range(sides):
            a,b,c,d = i,i+1,i+sides+2,i+sides+1
            uv=[tile_uv(5,u,v) for u,v in ((0,0),(1,0),(1,1),(0,1))]
            out.face([guard_points[j] for j in (a,c,b)],[uv[j] for j in (0,2,1)])
            out.face([guard_points[j] for j in (a,d,c)],[uv[j] for j in (0,3,2)])
    return out


def generate(age):
    asset=f'kr_tiger_hunter_a{age}'
    prior=ROOT/'authoring/art013/art/korea/units'/asset/(asset+'.blend')
    bpy.ops.wm.open_mainfile(filepath=str(prior),load_ui=False,use_scripts=False)
    rig, = [o for o in bpy.data.objects if o.type=='ARMATURE']
    originals = sorted((o for o in bpy.data.objects if o.type=='MESH'),key=lambda x:x.name)
    assert len(originals)==3
    folder = STAGE/'authoring'/asset
    material = bpy.data.materials.new(asset+'_atlas')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    for role in ('albedo','metalness','pattern'):
        image = bpy.data.images.load(str(folder/(role+'.png')))
        image.filepath = '//'+role+'.png'
        node = nodes.new('ShaderNodeTexImage')
        node.label=role
        node.image=image
        if role=='albedo':
            material.node_tree.links.new(node.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
        else:
            image.colorspace_settings.name='Non-Color'
    lods=[]
    for lod,original in enumerate(originals,1):
        surface=source_surface(original,age,lod)
        active={bone for weights in surface.weights for bone in weights}
        assert {g.name for v in original.data.vertices for g in (original.vertex_groups[x.group] for x in v.groups if x.weight>0)} <= active
        obj=make_mesh(surface,rig,material,asset+f'_lod{lod}',lod)
        lods.append(obj)
        bpy.data.objects.remove(original,do_unlink=True)
    for obj in lods[1:]:
        obj.hide_set(True)
        obj.hide_render=True
    for image in list(bpy.data.images):
        if not image.users:
            bpy.data.images.remove(image)
    bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
    rig.hide_set(False)
    bpy.context.view_layer.objects.active=lods[0]
    lods[0].select_set(True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/(asset+'.blend')),relative_remap=False)
    records=unit_export.skeleton_records(rig)
    n=len(records)
    assert n==48
    destination=STAGE/'exports'/asset
    destination.mkdir(parents=True,exist_ok=True)
    exporter['export_unit_model'](rig,lods[:1],destination/'model.fbx',records,
                                 three_lods=True,lod_counts=(n,n,n),lod_meshes={2:lods[1],3:lods[2]})
    native.write_rig(destination,native.rig_text(records,partitions=[('FullBody_LOD3',0,n)]))
    print('TIGER_EXPORT',asset,[len(o.data.polygons) for o in lods],flush=True)


for age in (2,3,4):
    generate(age)
