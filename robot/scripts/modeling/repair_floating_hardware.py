import bpy,math,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
H={};exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH18_FlushHardware_AndSupports');M=H['mats']()
if len(C.objects):raise RuntimeError('Attachment repair already applied')
OUT=Path(r'D:\codex+blender\model\robot\renders\reviews\attachment_repair_review');OUT.mkdir(exist_ok=True)
def hide(o):o.hide_render=True;o.hide_set(True)
def box(n,p,s,m='Frame',b=.005):return H['box'](n,p,s,C,M[m],b)
def plate(n,pts,y,d=.014,m='Ivory',b=.004):return H['prism_xz'](n,pts,y,d,C,M[m],bevel=b)
def mesh(n,v,f,m='Ivory'):
 ob=H['finish_mesh'](n,v,f,C,M[m],smooth=True)
 for md in list(ob.modifiers):
  if md.type=='WEIGHTED_NORMAL':ob.modifiers.remove(md)
 return ob
for o in list(bpy.data.objects):
 if o.hide_render:continue
 if o.name.startswith(('Ref16_Reactor','Arm_ForearmInnerPanel','Arm_ForearmOuterPanel','Arm_ForearmGoldCuff','Arm_ForearmBolt','Arm_ForearmVent','Arm_ForearmStatus','Ref16_ForearmPanelSplit','Ref16_ForearmGoldInlay','Target_UpperArmArmor','UpperArm_Core','Torso_LowerBolt')):hide(o)
# Reactor is one mounted cassette: back, integrated lip and thick recessed glass.
outer=[(-.061,1.213),(.061,1.213),(0,1.102)]
inner=[(-.044,1.2),(.044,1.2),(0,1.12)]
v=[];f=[]
for y,poly in [(-.133,outer),(-.103,outer),(-.133,inner),(-.103,inner)]:
 for x,z in poly:v.append((x,y,z))
for i in range(3):
 k=(i+1)%3;f.extend([(i,k,3+k,3+i),(i,6+i,6+k,k),(3+i,3+k,9+k,9+i),(6+i,9+i,9+k,6+k)])
ob=mesh('Attach_ReactorIntegratedBezel',v,f,'Visor')
md=H['modifier'](ob,'Bezel edge radius','BEVEL');md.width=.002;md.segments=3
plate('Attach_ReactorMount',outer,-.101,.038,'Frame',.003)
plate('Attach_ReactorRecessedLens',[(-.0445,1.2),(.0445,1.2),(0,1.119)],-.120,.014,'Cyan',.002)
# Structural waist bridge and shield bracket overlap both their supporting assemblies.
box('Attach_AbdomenStructuralBridge',(0,.005,.96),(.12,.12,.145),'Frame',.012)
box('Attach_PelvisShieldMount',(0,-.048,.854),(.108,.065,.12),'Frame',.008)
# Preserve the arm joint centers while replacing intersecting upper arm blocks.
for s,side in [(1,'L'),(-1,'R')]:
 a=Vector((s*.292,.012,1.166));b=Vector((s*.337,.003,1.022))
 H['segment_box']('Attach_UpperArmInnerSpar.'+side,a,b,.066,.074,C,M['Frame'],bevel=.008)
 center=(a+b)/2;quat=(a-b).to_track_quat('Z','Y');N=48
 sections=[(-.047,.037,.041),(-.039,.046,.049),(.022,.05,.053),(.04,.046,.047)]
 v=[];f=[]
 for z,rx,ry in sections:
  for i in range(N):
   th=2*math.pi*i/N;p=center+quat@Vector((rx*math.cos(th),ry*math.sin(th),z));v.append(tuple(p))
 for j in range(len(sections)-1):
  for i in range(N):
   aa=j*N+i;bb=j*N+(i+1)%N;f.append((aa,bb,bb+N,aa+N))
 # Two closed planar annuli, not smooth-shaded ngons crossing the internal spar.
 start=len(v)
 for z in [sections[0][0],sections[-1][0]]:
  for i in range(N):
   th=2*math.pi*i/N;v.append(tuple(center+quat@Vector((.031*math.cos(th),.035*math.sin(th),z))))
 for i in range(N):
  k=(i+1)%N;f.extend([(i,start+i,start+k,k),((len(sections)-1)*N+i,(len(sections)-1)*N+k,start+N+k,start+N+i),(start+i,start+N+i,start+N+k,start+k)])
 ob=mesh('Attach_CleanUpperArmSleeve.'+side,v,f)
 md=H['modifier'](ob,'Sleeve edge radius','BEVEL');md.width=.003;md.segments=3
bpy.context.view_layer.update()
D=bpy.context.evaluated_depsgraph_get()
def tree(name):
 o=bpy.data.objects[name];ev=o.evaluated_get(D);me=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@q.co for q in me.vertices],[list(p.vertices) for p in me.polygons]);ev.to_mesh_clear();return t
# Cast each panel vertex onto the actual forearm shell before adding thickness.
bolts=[];patch_targets=[]
for s,side in [(1,'L'),(-1,'R')]:
 target='Arm_ForearmShell.'+side;t=tree(target);v=[];f=[];nx=8
 rows=[(.842,.409,.023),(.86,.401,.031),(.89,.389,.035),(.92,.376,.031),(.943,.364,.022)]
 for z,cx,w in rows:
  for i in range(nx+1):
   x=s*(cx+w*(-1+2*i/nx));hit,normal,_,_=t.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)
   if hit is None:raise RuntimeError('Forearm projection missed '+side+' '+str((x,z)))
   v.append((hit.x,hit.y-.001,hit.z))
 for j in range(len(rows)-1):
  for i in range(nx):
   aa=j*(nx+1)+i;f.append((aa,aa+1,aa+nx+2,aa+nx+1))
 ob=mesh('Attach_ConformingForearmPanel.'+side,v,f)
 md=H['modifier'](ob,'Panel seats into base shell','SOLIDIFY');md.thickness=.003;md.offset=-1
 md=H['modifier'](ob,'Panel edge rounding','BEVEL');md.width=.001;md.segments=2
 patch_targets.append([ob.name,target])
 # Project two fastener positions, aligning their axis with the local surface normal.
 for i,(x,z) in enumerate([(s*.366,.929),(s*.409,.855)]):
  hit,n,_,_=t.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)
  if hit is None:raise RuntimeError('Bolt projection missed')
  # Base is 1 mm inside the support; head extends 3 mm outward.
  center=hit+n*.001
  bolt=H['cylinder']('Attach_ForearmBolt_'+str(i)+'.'+side,center,.004,.004,C,M['Gold'],axis=n,bevel=.001,segments=32)
  bolts.append({'object':bolt.name,'support':target,'base_embed_m':.001})
 # Fitted status light attaches to the new front patch.
 x=s*.389;z=.888;hit,n,_,_=t.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)
 housing=box('Attach_ForearmStatusHousing.'+side,hit+n*.003,(.031,.009,.012),'Frame',.003)
 box('Attach_ForearmStatusLens.'+side,hit+n*.008,(.02,.004,.006),'Cyan',.001)
# Re-seat remaining inherited chest fasteners on the actual curved chest.
t=tree('Ref16_CompoundChestShell')
for s,side in [(1,'L'),(-1,'R')]:
 x=s*.1;z=1.066
 hit,n,_,_=t.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)
 if hit is not None:
  ob=H['cylinder']('Attach_ChestBolt.'+side,hit+n*.001,.004,.004,C,M['Gold'],axis=n,bevel=.001,segments=32)
  bolts.append({'object':ob.name,'support':'Ref16_CompoundChestShell','base_embed_m':.001})
# Direct mounting check for inherited hip brace fasteners: keep them only if seated.
for side in ['L','R']:
 o=bpy.data.objects['Hip_BraceBolt.'+side];t=tree('Pelvis_DiagonalBrace.'+side)
 center=sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
 hit,n,_,_=t.ray_cast(Vector((center.x,-1,center.z)),Vector((0,1,0)),2)
 if hit is not None:
  shift=hit+n*.001-center;o.matrix_world.translation+=shift
 else:hide(o)
# Record new surface geometry after normals are made consistent.
for ob in C.objects:
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
bpy.context.view_layer.update()
(OUT/'fastener_mounts.json').write_text(json.dumps(bolts,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(Path('D:\\codex+blender\\model\\blender\\current\\robot_attachments_repaired.blend')))
print('Saved mounted reactor cassette, conforming forearm panels, projected bolts, clean arm sleeves and waist/shield supports.')
