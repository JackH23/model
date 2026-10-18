import bpy, math, json, bmesh
from pathlib import Path
from mathutils import Vector, Matrix
H={};exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
OUT=Path(r'D:\codex+blender\model\robot\renders\reviews\final_review');OUT.mkdir(exist_ok=True)
C=H['collection']('PH14_Complete_Refinement');M=H['mats']()
if len(C.objects):raise RuntimeError('Refinement already exists; do not apply transforms twice')
visible=[o for o in bpy.data.objects if o.type in ('MESH','CURVE') and not o.hide_render and not o.hide_get() and o.parent]
def hide(ob):ob.hide_render=True;ob.hide_set(True)
def box(n,p,s,m='Frame',b=.005):return H['box'](n,p,s,C,M[m],b)
def plate(n,pts,y,d=.02,m='Ivory',b=.006):return H['prism_xz'](n,pts,y,d,C,M[m],bevel=b)
def center(ob):return sum((ob.matrix_world@Vector(v) for v in ob.bound_box),Vector())/8
# Proportion changes move each mesh once, without re-transforming assembly parents.
for ob in visible:
 names={c.name for c in ob.users_collection};p=center(ob)
 if names.intersection({'PH12_Reference_Head','PH13_Head_ContinuousShell'}):
  ob.matrix_world=Matrix.Translation((0,0,-.025))@ob.matrix_world
 elif names.intersection({'PH5_Reference_Hands','PH6_Shoulder_Connections','PH8_Reference_ArmArmor','PH1_03_Arms'}) or ob.name.startswith(('Ear_NOT_USED','Elbow_','Wrist_','Shoulder_')):
  if abs(p.x)>.15:ob.matrix_world=Matrix.Translation((-.032 if p.x>0 else .032,0,0))@ob.matrix_world
 elif ob.name.startswith(('Leg_','Preview_','Thigh_','Shin_','Knee_','Ankle_','Hip_','Foot_','Toe_','Calf_','Pelvis_OuterHip')):
  if abs(p.x)>.08:ob.matrix_world=Matrix.Translation((-.032 if p.x>0 else .032,0,0))@ob.matrix_world
# Replace fragmented chest plates with a connected shell around a recessed reactor.
for ob in visible:
 if ob.name.startswith(('Torso_Pectoral','Torso_LowerChest','Torso_SideArmor','Torso_GoldCollar','Torso_GoldRib','Torso_Sternum','Torso_RibVent','Back_')):hide(ob)
outer=[(-.145,1.278),(.145,1.278),(.202,1.231),(.172,1.147),(.075,1.054),(-.075,1.054),(-.172,1.147),(-.202,1.231)]
inner=[(-.07,1.246),(.07,1.246),(.061,1.227),(.032,1.17),(0,1.114),(-.032,1.17),(-.061,1.227),(-.07,1.237)]
verts=[]
for poly,offset in [(outer,0),(inner,0),(outer,.035),(inner,.035)]:
 for x,z in poly:
  y=-.151+.032*(abs(x)/.202)**2
  verts.append((x,y+offset,z))
faces=[];n=8
for i in range(n):
 k=(i+1)%n;faces += [(i,k,n+k,n+i),(i,2*n+i,2*n+k,k),(n+i,n+k,3*n+k,3*n+i),(2*n+i,3*n+i,3*n+k,2*n+k)]
H['finish_mesh']('Final_ContinuousBreastplate',verts,faces,C,M['Ivory'],bevel=.008)
for s,side in [(1,'L'),(-1,'R')]:
 plate('Final_ChestGold.'+side,[(s*x,z) for x,z in [(.112,1.265),(.149,1.258),(.174,1.239),(.15,1.232),(.119,1.248)]],-.145,.012,'Gold',.003)
 # Fitted upper leg jacket covers most of the rectangular thigh core.
 H['loft']('Final_LowerThighShell.'+side,[(.588,.10,.115,s*.199,.0),(.626,.132,.15,s*.185,.008),(.69,.154,.174,s*.166,.014),(.726,.146,.167,s*.158,.022)],C,M['Ivory'],bevel=.015)
 plate('Final_ThighJointInset.'+side,[(s*x,z) for x,z in [(.165,.623),(.209,.63),(.226,.603),(.209,.58),(.178,.585)]],-.083,.016,'Frame',.005)
 # Sculpted shoulder lip reduces the hemisphere appearance and integrates the hub.
 plate('Final_ShoulderApron.'+side,[(s*x,z) for x,z in [(.252,1.292),(.3,1.318),(.371,1.302),(.414,1.263),(.405,1.217),(.371,1.198),(.312,1.209),(.269,1.245)]],-.098,.031,'Ivory',.012)
 plate('Final_ShoulderGold.'+side,[(s*x,z) for x,z in [(.367,1.219),(.402,1.235),(.407,1.216),(.382,1.199),(.366,1.201)]],-.118,.013,'Gold',.003)
 # Closely fitted shin overlay follows the actual rounded shell, rather than floating plates.
 sections=[(.235,.269,.014,.049,.06),(.3,.254,.013,.068,.083),(.38,.235,.015,.085,.096),(.447,.218,.011,.082,.092),(.478,.211,.003,.065,.076)]
 v=[];f=[];nu=18
 for z,cx,cy,rx,ry in sections:
  for i in range(nu+1):
   th=-math.pi*.92+math.pi*.84*i/nu
   v.append((s*(cx+(rx+.003)*math.cos(th)),cy+(ry+.003)*math.sin(th),z))
 for j in range(len(sections)-1):
  for i in range(nu):
   a=j*(nu+1)+i;f.append((a,a+1,a+nu+2,a+nu+1))
 ob=H['finish_mesh']('Final_FittedShinPlate.'+side,v,f,C,M['Ivory'],smooth=True)
 mod=H['modifier'](ob,'Fitted armor thickness','SOLIDIFY');mod.thickness=.004
 mod=H['modifier'](ob,'Shin contour smoothing','SUBSURF');mod.levels=2
 # Mechanical toe sections meet a fitted instep, with narrow dark joints.
 old=bpy.data.objects.get('Preview_IntegratedFootShell.'+side)
 if old:hide(old)
 for ob in visible:
  if ob.name.startswith('Preview_ToeSeam') and ob.name.endswith('.'+side):hide(ob)
 cx=s*.28
 H['loft']('Final_HeelInstep.'+side,[(.033,.163,.155,cx,.004),(.065,.174,.167,cx,.002),(.113,.147,.128,cx,.021),(.143,.102,.086,cx,.02)],C,M['Ivory'],bevel=.012)
 for i,dx in enumerate([-.054,0,.054]):
  x=cx+s*dx;w=.05;yf=-.171;yb=-.066
  v=[(x+xx,y,z) for xx,y,z in [(-w/2,yf,.03),(w/2,yf,.03),(w/2,yb,.03),(-w/2,yb,.03),(-w/2,yf,.066),(w/2,yf,.066),(w/2,yb,.099),(-w/2,yb,.099)]]
  H['finish_mesh']('Final_IntegratedToe_'+str(i)+'.'+side,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],C,M['Ivory'],bevel=.009)
  box('Final_ToeBumper_'+str(i)+'.'+side,(x,-.172,.044),(.024,.008,.022),'Gold',.003)
 # Fitted rear thorax panels and recessed central spine.
 plate('Final_BackArmor.'+side,[(s*x,z) for x,z in [(.026,1.267),(.128,1.268),(.179,1.224),(.149,1.131),(.08,1.083),(.033,1.115)]],.143,.024,'Ivory',.009)
 plate('Final_BackGold.'+side,[(s*x,z) for x,z in [(.119,1.251),(.151,1.23),(.157,1.207),(.14,1.215),(.115,1.239)]],.159,.01,'Gold',.003)
 box('Final_RearPelvis.'+side,(s*.061,.13,.856),(.097,.029,.092),'Ivory',.012)
for i in range(4):box('Final_BackSpine_'+str(i),(0,.158,1.119+i*.034),(.048,.026,.024),'Frame',.005)
box('Final_BackStatus',(0,.176,1.216),(.027,.008,.013),'Cyan',.002)
# Taper the rear head and reduce protrusion of its face surround.
for ob in visible:
 if ob.name.startswith(('RefHead_Visor','RefHead_Brow','RefHead_Jaw','RefHead_Cheek','RefHead_Eye','RefHead_Temple','RefHead_Chin')):
  ob.matrix_world=Matrix.Translation((0,.012,0))@ob.matrix_world
 if ob.name.startswith('RefHead_Antenna'):
  # Keep root attachment and slim the blade in its own mesh space.
  if ob.type=='MESH' and 'Root' not in ob.name:
   pts=[v.co.x for v in ob.data.vertices];mid=(min(pts)+max(pts))/2
   for v in ob.data.vertices:v.co.x=mid+(v.co.x-mid)*.84
# Consistent normals for new closed armor; preserve open backed armor intentionally.
for ob in C.objects:
 if ob.type=='MESH':
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
bpy.context.view_layer.update()
bpy.data.objects['Robot_Phase1']['refinement_pass']='All eight planned areas: proportion, continuous chest, thigh coverage, fitted shins and toes, shoulder aprons, integrated head, rear armor, surface normals.'
bpy.ops.wm.save_as_mainfile(filepath=str(Path('D:\\codex+blender\\model\\blender\\history\\robot_complete_refined.blend')))
print('Complete refinement saved; ready for multiview inspection.')
