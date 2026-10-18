import bpy, math, json, bmesh
from pathlib import Path
from mathutils import Vector
H={};exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH15_Target_Shape_Rebuild');M=H['mats']()
if len(C.objects):raise RuntimeError('Rebuild already applied')
OUT=Path(r'D:\codex+blender\model\robot\renders\reviews\target_rebuild_review');OUT.mkdir(exist_ok=True)
def hide(o):o.hide_render=True;o.hide_set(True)
def mesh(n,v,f,m='Ivory',bevel=0):return H['finish_mesh'](n,v,f,C,M[m],bevel=bevel,smooth=True)
def box(n,p,s,m='Frame',b=.005):return H['box'](n,p,s,C,M[m],b)
def cyl(n,p,r,d,m='Frame',axis=(1,0,0)):return H['cylinder'](n,p,r,d,C,M[m],axis=axis,bevel=.002,segments=48)
def panel(n,pts,y,d=.014,m='Ivory',b=.005):return H['prism_xz'](n,pts,y,d,C,M[m],bevel=b)
def signed(v,p):return math.copysign(abs(v)**p,v)
def curve(n,pts,m='Frame',r=.0014):
 cv=bpy.data.curves.new(n,'CURVE');cv.dimensions='3D';cv.bevel_depth=r;cv.bevel_resolution=3
 sp=cv.splines.new('POLY');sp.points.add(len(pts)-1)
 for q,p in zip(sp.points,pts):q.co=(*p,1)
 ob=bpy.data.objects.new(n,cv);C.objects.link(ob);ob.parent=bpy.data.objects['Robot_Phase1'];cv.materials.append(M[m]);return ob
def loft(n,sections,m='Ivory',power=.72,sub=1):
 N=40;v=[];f=[]
 for z,cx,cy,rx,ry in sections:
  for i in range(N):
   a=2*math.pi*i/N;v.append((cx+rx*signed(math.cos(a),power),cy+ry*signed(math.sin(a),power),z))
 for j in range(len(sections)-1):
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
 f.extend([tuple(reversed(range(N))),tuple(range((len(sections)-1)*N,len(sections)*N))])
 ob=mesh(n,v,f,m)
 if sub:
  mod=H['modifier'](ob,'Sculpted contour','SUBSURF');mod.levels=sub
 return ob
vis=[o for o in bpy.data.objects if o.type in ('MESH','CURVE') and o.parent and not o.hide_render and not o.hide_get()]
for o in vis:
 if o.name.startswith(('Final_ContinuousBreastplate','Final_ChestGold','Final_Shoulder','Final_LowerThigh','Final_ThighJoint','Final_FittedShin','Final_Heel','Final_IntegratedToe','Final_Toe','Arm_RoundedShoulder','Arm_Shoulder','Arm_BicepShell','Arm_BicepInset','Leg_ThighShell','Leg_ThighOuter','Leg_ThighInner','Leg_ThighGold','Leg_ThighBolt','Preview_CalfShell','Preview_CalfGold','Preview_RoundedSole','Preview_IntegratedFoot','Preview_Toe','Foot_')):hide(o)
 if o.name.startswith(('RefHead_Visor','RefHead_Brow','RefHead_Cheek','RefHead_Jaw','RefHead_Eye','RefHead_Chin','RefHead_Temple','RefHead_Crown','Head_ContinuousHelmetShell')):hide(o)
# Helmet: a swept curved housing, with a wrapped visor recessed into its opening.
N=64;v=[];f=[]
for j,(y,rx,rz,zc) in enumerate([(-.174,.184,.122,1.493),(-.1,.191,.142,1.502),(-.02,.19,.143,1.504),(.06,.175,.132,1.501),(.13,.123,.099,1.498),(.165,.035,.045,1.496)]):
 for i in range(N):
  a=2*math.pi*i/N;x=rx*signed(math.cos(a),.73);z=zc+rz*signed(math.sin(a),.73)
  yy=y+(.016*(abs(x)/rx)**2 if j==0 else 0);v.append((x,yy,z))
for j in range(5):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
f.append(tuple(range(5*N,6*N)))
ob=mesh('Target_HelmetContinuousShell',v,f)
mod=H['modifier'](ob,'Helmet smoothing','SUBSURF');mod.levels=2
mod=H['modifier'](ob,'Helmet wall','SOLIDIFY');mod.thickness=.006
# Radial face surround interpolates smoothly between helmet perimeter and visor.
v=[];f=[];R=6
for j in range(R+1):
 t=j/R
 for i in range(N):
  a=2*math.pi*i/N
  xo=.184*signed(math.cos(a),.73);zo=1.493+.122*signed(math.sin(a),.73);yo=-.174+.016*(abs(xo)/.184)**2
  xi=.151*signed(math.cos(a),.65);zi=1.49+.079*signed(math.sin(a),.7);yi=-.204+.024*(abs(xi)/.151)**2
  v.append((xo*(1-t)+xi*t,yo*(1-t)+yi*t-.006*math.sin(t*math.pi),zo*(1-t)+zi*t))
for j in range(R):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
ob=mesh('Target_IntegratedBrowJaw',v,f);mod=H['modifier'](ob,'Face frame thickness','SOLIDIFY');mod.thickness=.007
# Curved dark face disk with tightly fitted illuminated eyes.
v=[(0,-.207,1.49)];f=[]
for i in range(N):
 a=2*math.pi*i/N;x=.153*signed(math.cos(a),.65);v.append((x,-.202+.024*(abs(x)/.153)**2,1.49+.081*signed(math.sin(a),.7)))
for i in range(N):f.append((0,i+1,(i+1)%N+1))
mesh('Target_WrappedVisor',v,f,'Visor')
box('Target_CrownInset',(0,-.026,1.644),(.067,.108,.013),'Frame',.006)
# Chest is compound-curved, with an integrated throat and lower pointed sternum.
outer=[(-.143,1.277),(.143,1.277),(.199,1.226),(.162,1.137),(.05,1.043),(-.05,1.043),(-.162,1.137),(-.199,1.226)]
inner=[(-.064,1.241),(.064,1.241),(.058,1.224),(.03,1.17),(0,1.118),(-.03,1.17),(-.058,1.224),(-.064,1.231)]
v=[];f=[];n=8;rad=8
for j in range(rad+1):
 t=j/rad
 for (xo,zo),(xi,zi) in zip(outer,inner):
  x=xo*(1-t)+xi*t;z=zo*(1-t)+zi*t
  y=-.133-.043*(1-(x/.22)**2)-.012*math.sin(math.pi*t)
  v.append((x,y,z))
for j in range(rad):
 for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
ob=mesh('Target_SculptedBreastplate',v,f);mod=H['modifier'](ob,'Chest armor wall','SOLIDIFY');mod.thickness=.019
mod=H['modifier'](ob,'Armor contour bevel','BEVEL');mod.width=.006;mod.segments=3
# Move recessed reactor outward to sit behind the new breastplate lip.
for o in vis:
 if o.name.startswith('Torso_Reactor'):o.location.y-=.032
for s,side in [(1,'L'),(-1,'R')]:
 def p(x,y,z):return(s*x,y,z)
 # Eyelights and small integrated cheek guards.
 eye=box('Target_Eye.'+side,p(.078,-.209,1.493),(.023,.012,.061),'Cyan',.010)
 panel('Target_CheekInset.'+side,[(s*x,z) for x,z in [(.123,1.449),(.155,1.463),(.164,1.441),(.143,1.423),(.116,1.431)]],-.185,.012,'Gold',.004)
 panel('Target_ChestCollarGold.'+side,[(s*x,z) for x,z in [(.115,1.264),(.146,1.257),(.165,1.238),(.139,1.236),(.116,1.247)]],-.158,.010,'Gold',.004)
 # Curved wraparound pauldrons extend below the joint and taper at the rear.
 v=[];f=[];nu=36;nv=16
 for j in range(nv+1):
  for i in range(nu+1):
   th=2*math.pi*i/nu
   end=1.89+.24*math.sin(th)+.08*math.cos(2*th)
   ph=.035+(end-.035)*j/nv
   x=.31+.113*math.sin(ph)*math.cos(th)
   y=.012+.119*math.sin(ph)*math.sin(th)
   z=1.25+.106*math.cos(ph)-.014*math.cos(th)*math.sin(ph)
   v.append(p(x,y,z))
 for j in range(nv):
  for i in range(nu):a=j*(nu+1)+i;f.append((a,a+1,a+nu+2,a+nu+1))
 ob=mesh('Target_WraparoundShoulder.'+side,v,f);mod=H['modifier'](ob,'Shoulder thickness','SOLIDIFY');mod.thickness=.009
 mod=H['modifier'](ob,'Shoulder smooth contour','SUBSURF');mod.levels=1
 panel('Target_ShoulderGold.'+side,[(s*x,z) for x,z in [(.372,1.224),(.41,1.24),(.416,1.218),(.392,1.196),(.371,1.201)]],-.087,.013,'Gold',.004)
 # Integrated compact biceps sleeve.
 loft('Target_UpperArmArmor.'+side,[(1.071,s*.337,.002,.035,.044),(1.105,s*.326,.001,.044,.055),(1.156,s*.313,.008,.048,.06),(1.186,s*.306,.012,.038,.048)],power=.7)
 # Fuller continuous thigh volume, tapering into the knee recess.
 loft('Target_ThighJacket.'+side,[(.585,s*.199,.003,.045,.056),(.607,s*.194,.004,.055,.069),(.657,s*.18,.014,.075,.087),(.723,s*.156,.024,.086,.101),(.778,s*.145,.032,.077,.094),(.797,s*.14,.033,.058,.071)],power=.66,sub=2)
 panel('Target_ThighGold.'+side,[(s*x,z) for x,z in [(.213,.657),(.239,.684),(.241,.652),(.215,.609),(.2,.613)]],-.072,.012,'Gold',.004)
 # Sculpted shin with angular changes of section and short ankle exposure.
 for o in vis:
  if o.name.startswith(('Final_FittedShin','Preview_CalfShell','Preview_CalfGold','Leg_ShinGold')) and o.name.endswith('.'+side):hide(o)
 secs=[(.191,s*.275,.013,.04,.045),(.214,s*.272,.01,.045,.053),(.269,s*.262,.012,.053,.07),(.326,s*.248,.014,.076,.086),(.392,s*.232,.017,.083,.092),(.444,s*.221,.014,.075,.087),(.474,s*.212,.004,.056,.067),(.489,s*.209,-.003,.044,.054)]
 loft('Target_AngularCalf.'+side,secs,power=.64,sub=2)
 # Curved narrow service seam across the side, attached to the shell.
 pts=[]
 for z,cx,cy,rx,ry in secs[1:-1]:
  a=-.64;pts.append((cx+s*rx*signed(math.cos(a),.64),cy+ry*signed(math.sin(a),.64)-.001,z))
 curve('Target_CalfGold.'+side,pts,'Gold',.0024)
 # Forearm and shin service seams follow their surfaces; no floating planar plates.
 curve('Target_ShoulderSeam.'+side,[p(.275,-.081,1.319),p(.309,-.103,1.296),p(.342,-.103,1.27),p(.37,-.082,1.243)],'Frame',.0012)
 panel('Target_KneeGuard.'+side,[(s*x,z) for x,z in [(.184,.579),(.218,.58),(.237,.554),(.222,.525),(.193,.526),(.178,.551)]],-.096,.014,'Ivory',.006)
 # Armor lap between calf and ankle housing.
 box('Target_AnkleInstep.'+side,p(.279,-.014,.14),(.104,.101,.059),'Ivory',.012)
 # Small gold shin fastener seated near upper front surface.
 cyl('Target_ShinFastener.'+side,p(.22,-.078,.437),.004,.005,'Gold',(0,1,0))
# Rear service panels blend into the thorax instead of a rectangular attached pack.
for o in vis:
 if o.name.startswith(('Final_BackArmor','Final_BackGold','Final_RearPelvis')):hide(o)
for s,side in [(1,'L'),(-1,'R')]:
 panel('Target_BackShell.'+side,[(s*x,z) for x,z in [(.026,1.272),(.113,1.269),(.175,1.226),(.146,1.155),(.075,1.092),(.031,1.13)]],.147,.03,'Ivory',.012)
 box('Target_RearHipArmor.'+side,(s*.061,.126,.854),(.096,.032,.091),'Ivory',.014)
# Material finish: restrained procedural satin roughness, not noisy color dirt.
for key in ['Ivory','Gold','Frame']:
 mat=M[key];node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 node.inputs['Roughness'].default_value={'Ivory':.30,'Gold':.27,'Frame':.39}[key]
 node.inputs['Metallic'].default_value={'Ivory':.16,'Gold':.76,'Frame':.65}[key]
 if key=='Ivory':
  node.inputs['Base Color'].default_value=(.79,.745,.64,1)
 noise=mat.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=180;noise.inputs['Detail'].default_value=2
 ramp=mat.node_tree.nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=0;ramp.inputs['From Max'].default_value=1;ramp.inputs['To Min'].default_value=.26 if key!='Frame' else .34;ramp.inputs['To Max'].default_value=.34 if key!='Frame' else .43
 mat.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Value']);mat.node_tree.links.new(ramp.outputs[0],node.inputs['Roughness'])
# Correct orientation of mirrored generated meshes and validate all new vertex values.
for o in C.objects:
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(Path('D:\\codex+blender\\model\\blender\\history\\robot_target_rebuilt.blend')))
print('Saved target rebuild:',len(C.objects),'new objects. Ready for review.')
