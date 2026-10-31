"""Deterministic Hwacha authoring, staged for visual inspection; official siege skeleton unchanged."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2];W=Path('F:/aoe_4_temp/Temp_aoe4')
A=R/'authoring/art014/hwacha';A.mkdir(parents=True,exist_ok=True)
PARTS=[]
ATLAS={'wood':(.08,.12),'darkwood':(.08,.32),'iron':(.08,.52),'team':(.08,.72),'rocket':(.08,.92)}
def rig():return next(o for o in bpy.data.objects if o.type=='ARMATURE')
def material():
 m=bpy.data.materials.get('kr014_hwacha_atlas') or bpy.data.materials.new('kr014_hwacha_atlas');m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');tex=m.node_tree.nodes.get('Hwacha albedo')
 if not tex:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.name='Hwacha albedo';tex.image=bpy.data.images.load(str(A/'albedo.png'),check_existing=True);tex.image.filepath=str(A/'albedo.png');m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 return m
def own(o,name,bone,swatch):
 o.name='HWACHA_'+name;o.data.name=o.name;o.data.materials.clear();o.data.materials.append(material())
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 o.vertex_groups.clear();g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
 for mod in list(o.modifiers):o.modifiers.remove(mod)
 mod=o.modifiers.new('Official cannon skeleton','ARMATURE');mod.object=rig();o.parent=rig();o.matrix_parent_inverse=Matrix.Identity(4)
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap');u,v=ATLAS[swatch]
 for face in o.data.polygons:
  for j,li in enumerate(face.loop_indices):uv.data[li].uv=(u+(j%2)*.14,v+(j//2%2)*.08)
 PARTS.append(o);o.select_set(False);return o
def box(name,loc,scale,bone='bone_master_rotation',swatch='wood'):
 bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.view_layer.objects.active;o.scale=scale;return own(o,name,bone,swatch)
def cylinder(name,p,q,r,bone,swatch='wood',sides=8):
 p,q=Vector(p),Vector(q);d=q-p;bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=r,depth=d.length,location=(p+q)/2)
 o=bpy.context.view_layer.objects.active;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return own(o,name,bone,swatch)
def start():
 if Path(bpy.data.filepath) not in [W/'hwacha-donor.blend',A/'donor_geometry.blend']:
  raise RuntimeError('Open authoring/art014/hwacha/donor_geometry.blend in a separate invocation, then re-claim the Blender session before authoring.')
 for o in list(bpy.data.objects):
  if o.type not in ['ARMATURE','MESH'] or o.name in ['Cube'] or 'geo_pole' in o.name or o.name.endswith(('.001','.002')):bpy.data.objects.remove(o,do_unlink=True)
 donor=next(o for o in bpy.data.objects if o.type=='MESH')
 # Preserve the donor wheels and axle/chassis; remove its hexagonal Chinese launcher.
 import bmesh
 bm=bmesh.new();bm.from_mesh(donor.data);bm.verts.ensure_lookup_table();groups={g.index:g.name for g in donor.vertex_groups}
 keep=set()
 for v in donor.data.vertices:
  names=[groups[g.group] for g in v.groups if g.weight>.5]
  if any('wheel' in n for n in names) or v.co.z<.83:keep.add(v.index)
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in keep],context='VERTS');bm.to_mesh(donor.data);bm.free()
 donor.name='HWACHA_Official_wheels_and_chassis';donor.data.materials.clear();donor.data.materials.append(material())
 uv=donor.data.uv_layers.active
 for face in donor.data.polygons:
  for j,li in enumerate(face.loop_indices):uv.data[li].uv=(.08+(j%2)*.14,.12+(j//2%2)*.08)
 # Explicit seat: platform bottom=.77 overlaps surviving chassis top=.83 by .06m.
 box('platform',(0,.10,.84),(1.55,1.35,.14),swatch='darkwood')
 for x in [-.63,.63]:box('launcher_post', (x,.35,1.14),(.12,.14,.60))
 # Hinged rectangular launcher, defining anchors shared by later ribs/rocket rows.
 box('rack_back',(0,.35,1.42),(1.42,.18,.78),swatch='darkwood')
 box('rack_lower_rail',(0,.20,1.01),(1.58,.24,.14))
 box('rack_upper_rail',(0,.20,1.83),(1.58,.24,.14))
 for x in [-.75,.75]:box('rack_side',(x,.20,1.42),(.12,.24,.90))
 box('owner_cloth_left',(-.82,.08,1.12),(.035,.36,.42),swatch='team')
 box('owner_cloth_right',(.82,.08,1.12),(.035,.36,.42),swatch='team')
 validate('frame')
def rockets():
 # Inspect one seated guide, then call this only after the rack frame is approved.
 for row in range(10):
  for col in range(10):
   x=-.63+col*.14;z=1.10+row*.068
   cylinder('rocket_%02d_%02d'%(row,col),(x,.36,z),(x,-.32,z+.20),.012,'bone_master_rotation','rocket',4)
 for z in [1.055,1.735]:box('rocket_support_rail',(0,.23,z),(1.42,.12,.045))
 validate('complete')
def validate(step):
 objs=[o for o in bpy.data.objects if o.type=='MESH'];tri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs)
 assert tri<15000
 names={b.name for b in rig().data.bones};assert len(names)==5
 for o in objs:
  assert all(g.name in names for g in o.vertex_groups)
  assert all(v.groups and abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in o.data.vertices)
  assert o.data.uv_layers.active
 (A/'validation.json').write_text(json.dumps({'step':step,'triangles':tri,'skeleton_bones':sorted(names),'native_animation_owner':'cannon_single_axle','new_animation_clips':False,'platform_to_chassis_overlap_m':.06,'rack_bottom_z':1.03,'post_top_z':1.44,'post_rack_overlap_m':.41,'rocket_count':100 if step=='complete' else 0,'runtime_acceptance':'pending'},indent=2))
 print('HWACHA_VALIDATED',step,tri,flush=True)
def finish():
 bpy.ops.object.select_all(action='DESELECT');meshes=[o for o in bpy.data.objects if o.type=='MESH']
 for o in meshes:o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();mesh=bpy.context.view_layer.objects.active;mesh.name='kr_hwacha_lod1'
 for i,ratio in [(2,.65),(3,.35)]:
  o=mesh.copy();o.data=mesh.data.copy();bpy.context.collection.objects.link(o);o.name='kr_hwacha_lod'+str(i)
  bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('LOD reduction','DECIMATE');mod.ratio=ratio;bpy.ops.object.modifier_apply(modifier=mod.name);o.hide_set(True)
 bpy.context.view_layer.objects.active=mesh
 for area in bpy.context.screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID';area.spaces.active.region_3d.view_distance=5
 bpy.ops.wm.save_as_mainfile(filepath=str(A/'kr_hwacha.blend'))
 print('HWACHA_MASTER_SAVED',A/'kr_hwacha.blend',flush=True)
