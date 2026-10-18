import bpy,math,bmesh,json
from pathlib import Path
from mathutils import Vector
H={};exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH17_ShoulderChestHelmet_Finish');M=H['mats']()
if len(C.objects):raise RuntimeError('Pass already applied')
OUT=Path(r'D:\codex+blender\model\robot\renders\reviews\assembly_finish_review');OUT.mkdir(exist_ok=True)
def hide(o):o.hide_render=True;o.hide_set(True)
def mesh(n,v,f,m='Ivory'):
 ob=H['finish_mesh'](n,v,f,C,M[m],smooth=True)
 for mod in list(ob.modifiers):
  if mod.type=='WEIGHTED_NORMAL':ob.modifiers.remove(mod)
 return ob
def signed(v,p):return math.copysign(abs(v)**p,v)
# Seat actual bearing housings in the shoulder armor, replacing detached discs.
for s,side in [(1,'L'),(-1,'R')]:
 for stem in ['Shoulder_OuterHub','Shoulder_HubRim','Shoulder_HubInset','Shoulder_HubCenter']:
  hide(bpy.data.objects[stem+'.'+side])
 H['cylinder']('Finish_ShoulderAxle.'+side,(s*.378,.014,1.225),.047,.106,C,M['Frame'],axis=(1,0,0),bevel=.002,segments=64)
 H['cylinder']('Finish_ShoulderSocket.'+side,(s*.401,.014,1.225),.063,.034,C,M['Frame'],axis=(1,0,0),bevel=.003,segments=64)
 H['ring']('Finish_ShoulderBearingRim.'+side,(s*.419,.014,1.225),.059,.047,.009,C,M['Gold'],axis=(1,0,0))
 H['cylinder']('Finish_ShoulderBearingInset.'+side,(s*.424,.014,1.225),.046,.008,C,M['Frame'],axis=(1,0,0),bevel=.002,segments=64)
 H['ring']('Finish_ShoulderInnerBezel.'+side,(s*.429,.014,1.225),.036,.03,.004,C,M['Visor'],axis=(1,0,0))
# Compress only the front half of the thorax and its attached trim, retaining rear support.
for o in bpy.data.objects:
 if o.hide_render or o.type not in ('MESH','CURVE'):continue
 if o.name.startswith(('Ref16_CompoundChest','Ref16_Chest','Ref16_Reactor')):
  if o.type=='MESH':
   for vert in o.data.vertices:
    w=o.matrix_world@vert.co
    if w.y<0:w.y*=.78
    vert.co=o.matrix_world.inverted()@w
  else:
   for sp in o.data.splines:
    for q in sp.points:
     w=o.matrix_world@Vector(q.co[:3])
     if w.y<0:w.y*=.78
     p=o.matrix_world.inverted()@w;q.co=(*p,1)
# Hide low-resolution helmet surfaces and radial-fan visor.
for n in ['Ref16_HelmetHousing','Ref16_IntegratedFaceArmor','Ref16_VisorGlass','Ref16_HelmetCenterSeam']:
 hide(bpy.data.objects[n])
# A square-to-rounded-perimeter mapping gives matching grid boundaries and no rear ngon.
K=16
perimeter=[]
for i in range(K):perimeter.append((-1+2*i/K,-1))
for i in range(K):perimeter.append((1,-1+2*i/K))
for i in range(K):perimeter.append((1-2*i/K,1))
for i in range(K):perimeter.append((-1,1-2*i/K))
N=len(perimeter)
def mapped(u,v,power=.72):
 x=u*math.sqrt(max(0,1-v*v/2));z=v*math.sqrt(max(0,1-u*u/2))
 return signed(x,power),signed(z,power)
cz=1.484
sections=[(-.168,.183,.12),(-.115,.192,.136),(-.035,.193,.142),(.045,.185,.137),(.105,.17,.126),(.137,.155,.115)]
verts=[];faces=[]
for j,(y,rx,rz) in enumerate(sections):
 for u,v in perimeter:
  x,z=mapped(u,v);verts.append((rx*x,y,cz+rz*z))
for j in range(len(sections)-1):
 for i in range(N):
  a=j*N+i;b=j*N+(i+1)%N;faces.append((a,b,b+N,a+N))
start=len(verts)
for j in range(K+1):
 v=-1+2*j/K
 for i in range(K+1):
  u=-1+2*i/K;x,z=mapped(u,v)
  verts.append((.155*x,.137+.036*(1-u*u)*(1-v*v),cz+.115*z))
for j in range(K):
 for i in range(K):
  a=start+j*(K+1)+i;faces.append((a,a+1,a+K+2,a+K+1))
ob=mesh('Finish_QuadHelmetHousing',verts,faces)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
mod=H['modifier'](ob,'Quad surface refinement','SUBSURF');mod.levels=2
mod=H['modifier'](ob,'Helmet wall thickness','SOLIDIFY');mod.thickness=.006
# Matching quad strips blend the brow and jaw into the helmet boundary.
verts=[];faces=[];R=8
for j in range(R+1):
 t=j/R
 for u,v in perimeter:
  x,z=mapped(u,v)
  xo=.183*x;zo=cz+.12*z
  xi=.147*x;zi=1.488+.08*z
  yi=-.205+.025*x*x
  verts.append((xo*(1-t)+xi*t,-.168*(1-t)+yi*t-.004*math.sin(math.pi*t),zo*(1-t)+zi*t))
for j in range(R):
 for i in range(N):
  a=j*N+i;b=j*N+(i+1)%N;faces.append((a,b,b+N,a+N))
ob=mesh('Finish_QuadBrowJawSurround',verts,faces)
mod=H['modifier'](ob,'Face armor thickness','SOLIDIFY');mod.thickness=.008
# Continuous all-quad glass grid removes triangular-fan highlight ripples.
verts=[];faces=[]
for j in range(K+1):
 v=-1+2*j/K
 for i in range(K+1):
  u=-1+2*i/K;x,z=mapped(u,v)
  verts.append((.148*x,-.205+.025*x*x-.002*(1-u*u)*(1-v*v),1.488+.081*z))
for j in range(K):
 for i in range(K):
  a=j*(K+1)+i;faces.append((a,a+1,a+K+2,a+K+1))
ob=mesh('Finish_QuadCurvedVisor',verts,faces,'Visor')
mod=H['modifier'](ob,'Glass smoothing','SUBSURF');mod.levels=1
# Re-seat eyes and cheek guards against new curved face.
for side in ['L','R']:
 eye=bpy.data.objects['Ref16_Eye.'+side];world=eye.matrix_world.copy();world.translation.y=-.207;eye.matrix_world=world
# Recalculate source normals for newly generated mirrored closed bearings.
for ob in C.objects:
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(Path('D:\\codex+blender\\model\\blender\\history\\robot_assembly_finished.blend')))
print('Rebuilt helmet and visor using quad surfaces; seated both shoulder bearings; reduced chest projection by 22 percent.')
