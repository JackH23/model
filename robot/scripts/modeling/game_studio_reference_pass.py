import bpy, math, json, bmesh
from pathlib import Path
from mathutils import Vector
H={};exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH16_Reference_Armor_Construction');M=H['mats']()
if len(C.objects):raise RuntimeError('Reference pass already exists')
OUT=Path(r'D:\codex+blender\model\robot\renders\reviews\reference_construction_review');OUT.mkdir(exist_ok=True)
def hide(o):o.hide_render=True;o.hide_set(True)
def mesh(n,v,f,m='Ivory',bev=0):return H['finish_mesh'](n,v,f,C,M[m],bevel=bev,smooth=True)
def plate(n,pts,y,d=.014,m='Ivory',b=.004):return H['prism_xz'](n,pts,y,d,C,M[m],bevel=b)
def box(n,p,s,m='Frame',b=.005):return H['box'](n,p,s,C,M[m],b)
def cyl(n,p,r,d,m='Frame',axis=(1,0,0)):return H['cylinder'](n,p,r,d,C,M[m],axis=axis,bevel=.0015,segments=48)
def signed(v,p):return math.copysign(abs(v)**p,v)
def curve(n,pts,m='Frame',r=.0011):
 cv=bpy.data.curves.new(n,'CURVE');cv.dimensions='3D';cv.bevel_depth=r;cv.bevel_resolution=3;sp=cv.splines.new('POLY');sp.points.add(len(pts)-1)
 for q,p in zip(sp.points,pts):q.co=(*p,1)
 ob=bpy.data.objects.new(n,cv);C.objects.link(ob);ob.parent=bpy.data.objects['Robot_Phase1'];cv.materials.append(M[m]);return ob
def thickness(ob,d=.006):
 mod=H['modifier'](ob,'Armor wall thickness','SOLIDIFY');mod.thickness=d
 mod=H['modifier'](ob,'Machined armor edges','BEVEL');mod.width=.002;mod.segments=3
def link(n,a,b,w,d,m='Frame'):return H['segment_box'](n,a,b,w,d,C,M[m],bevel=.003)
visible=[o for o in bpy.data.objects if o.parent and not o.hide_render and not o.hide_get()]
for o in visible:
 if o.name.startswith(('Target_Helmet','Target_IntegratedBrow','Target_WrappedVisor','Target_Crown','Target_Eye','Target_Cheek','Target_SculptedBreast','Target_ChestWrap','Target_ChestCollar','Torso_Reactor','Target_AngularCalf','Target_CalfGold','Target_ShinFastener','Target_WraparoundShoulder','Target_ShoulderGold','Target_ShoulderSeam','Target_KneeGuard','Target_ThighGold')):hide(o)
# New helmet uses an angular brow/jaw contour with a wrapped glass face.
outer=[(-.09,1.626),(.09,1.626),(.158,1.596),(.181,1.553),(.175,1.451),(.107,1.384),(-.107,1.384),(-.175,1.451),(-.181,1.553),(-.158,1.596)]
inner=[(-.083,1.574),(.083,1.574),(.138,1.555),(.151,1.529),(.139,1.468),(.085,1.436),(-.085,1.436),(-.139,1.468),(-.151,1.529),(-.138,1.555)]
N=len(outer);v=[];f=[]
for j,(y,sx,sz) in enumerate([(-.168,1,1),(-.09,1.055,1.075),(.015,1.04,1.08),(.09,.89,.98),(.15,.59,.71),(.178,.2,.32)]):
 for x,z in outer:v.append((x*sx,y,1.502+(z-1.502)*sz))
for j in range(5):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
f.append(tuple(range(5*N,6*N)))
ob=mesh('Ref16_HelmetHousing',v,f,bev=.009);thickness(ob)
v=[];f=[];R=5
for j in range(R+1):
 t=j/R
 for (xo,zo),(xi,zi) in zip(outer,inner):
  x=xo*(1-t)+xi*t;z=zo*(1-t)+zi*t
  y=-.168*(1-t)+(-.211+.033*(abs(xi)/.151)**2)*t-.01*math.sin(math.pi*t)
  v.append((x,y,z))
for j in range(R):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;f.append((a,b,b+N,a+N))
ob=mesh('Ref16_IntegratedFaceArmor',v,f,bev=.005);thickness(ob,.009)
# Curved glass surface and slim eye lenses; all seated behind the armor edge.
v=[(0,-.211,1.507)];f=[]
for x,z in inner:v.append((x,-.204+.033*(abs(x)/.151)**2,z))
for i in range(N):f.append((0,i+1,(i+1)%N+1))
mesh('Ref16_VisorGlass',v,f,'Visor')
box('Ref16_CrownVent',(0,-.023,1.641),(.066,.096,.013),'Frame',.006)
curve('Ref16_HelmetCenterSeam',[(0,-.159,1.628),(0,-.09,1.641),(0,.015,1.642),(0,.075,1.631)])
# Cast chest armor: rays match the outer silhouette to the triangular recess.
outerch=[(-.132,1.276),(.132,1.276),(.189,1.232),(.169,1.157),(.065,1.057),(0,1.04),(-.065,1.057),(-.169,1.157),(-.189,1.232)]
tri=[(-.057,1.237),(.057,1.237),(0,1.133)];origin=Vector((0,1.19))
def ray(poly,angle):
 d=Vector((math.cos(angle),math.sin(angle)));hits=[]
 for i,a in enumerate(poly):
  a=Vector(a)-origin;b=Vector(poly[(i+1)%len(poly)])-origin;e=b-a
  den=d.x*e.y-d.y*e.x
  if abs(den)<1e-9:continue
  t=(a.x*e.y-a.y*e.x)/den;u=(a.x*d.y-a.y*d.x)/den
  if t>0 and -.00001<=u<=1.00001:hits.append(t)
 return origin+d*min(hits)
NC=96;R=8;v=[];f=[]
for j in range(R+1):
 t=j/R
 for i in range(NC):
  a=2*math.pi*i/NC;o=ray(outerch,a);inn=ray(tri,a);p=o*(1-t)+inn*t;x,z=p
  y=-.109-.04*(1-(x/.20)**2)-.013*math.sin(t*math.pi)
  v.append((x,y,z))
for j in range(R):
 for i in range(NC):a=j*NC+i;b=j*NC+(i+1)%NC;f.append((a,b,b+NC,a+NC))
# Continuous side walls, matching the surface perimeter exactly.
start=len(v)
for i in range(NC):
 a=2*math.pi*i/NC;x,z=ray(outerch,a);v.append((x*.9,.117,1.16+(z-1.16)*.98))
for i in range(NC):k=(i+1)%NC;f.append((i,start+i,start+k,k))
ob=mesh('Ref16_CompoundChestShell',v,f);thickness(ob,.012)
plate('Ref16_ReactorSocket',tri,-.155,.025,'Frame',.006)
plate('Ref16_ReactorLens',[(-.043,1.227),(.043,1.227),(0,1.148)],-.172,.007,'Cyan',.004)
for i,(a,b) in enumerate(zip([(-.051,-.18,1.232),(.051,-.18,1.232),(0,-.18,1.14)],[ (.051,-.18,1.232),(0,-.18,1.14),(-.051,-.18,1.232)])):
 link('Ref16_ReactorRim_'+str(i),a,b,.006,.008,'Visor')
# Bilateral armor construction with surface-following detail.
for s,side in [(1,'L'),(-1,'R')]:
 def p(x,y,z):return(s*x,y,z)
 def panel(n,pts,y,d=.014,m='Ivory',b=.004):return plate(n+'.'+side,[(s*x,z) for x,z in pts],y,d,m,b)
 eye=box('Ref16_Eye.'+side,p(.076,-.214,1.506),(.022,.012,.064),'Cyan',.009)
 eye.rotation_euler.y=s*math.radians(-7)
 panel('Ref16_CheekGuard',[(.102,1.458),(.143,1.472),(.164,1.451),(.139,1.421),(.103,1.43)],-.178,.018)
 panel('Ref16_CheekGold',[(.135,1.46),(.153,1.468),(.164,1.449),(.146,1.436)],-.191,.008,'Gold',.002)
 panel('Ref16_JawCenter',[(.0,1.43),(.055,1.441),(.085,1.42),(.053,1.39),(0,1.388)],-.193,.025)
 panel('Ref16_ChestGold',[(.115,1.266),(.144,1.257),(.162,1.237),(.139,1.237),(.117,1.248)],-.137,.011,'Gold')
 curve('Ref16_ChestPanelLine.'+side,[p(.108,-.145,1.26),p(.13,-.139,1.229),p(.151,-.131,1.204),p(.152,-.131,1.179)])
 # Shoulder compound shell: uneven lower rim wraps around joint and exposes biceps.
 nu=48;nv=18;v=[];f=[]
 for j in range(nv+1):
  for i in range(nu+1):
   a=2*math.pi*i/nu;end=1.9+.27*math.sin(a)+.14*math.cos(2*a);ph=.03+(end-.03)*j/nv
   v.append(p(.307+.113*math.sin(ph)*math.cos(a),.014+.116*math.sin(ph)*math.sin(a),1.25+.106*math.cos(ph)-.018*math.cos(a)*math.sin(ph)))
 for j in range(nv):
  for i in range(nu):a=j*(nu+1)+i;f.append((a,a+1,a+nu+2,a+nu+1))
 ob=mesh('Ref16_SculptedPauldron.'+side,v,f);thickness(ob,.008)
 # Gold shoulder inset follows the cap curvature, instead of a corner block.
 pts=[]
 for t in range(18):
  ph=.3+1.24*t/17;a=-.48;pts.append(p(.307+.115*math.sin(ph)*math.cos(a),.014+.118*math.sin(ph)*math.sin(a),1.25+.108*math.cos(ph)-.018*math.cos(a)*math.sin(ph)))
 curve('Ref16_ShoulderGoldInlay.'+side,pts,'Gold',.005)
 # Calf shell with actual knee and ankle access cutouts, revealing inset mechanisms.
 secs=[(.192,.275,.013,.04,.046),(.22,.269,.011,.047,.058),(.272,.259,.012,.058,.075),(.33,.247,.014,.077,.087),(.392,.232,.016,.083,.093),(.442,.221,.014,.078,.09),(.476,.211,.004,.058,.069),(.49,.208,-.003,.044,.055)]
 n=64;v=[];f=[]
 for z,cx,cy,rx,ry in secs:
  for i in range(n):
   a=2*math.pi*i/n;v.append(p(cx+rx*signed(math.cos(a),.62),cy+ry*signed(math.sin(a),.62),z))
 for j in range(len(secs)-1):
  for i in range(n):
   a=2*math.pi*(i+.5)/n;front=math.sin(a)<-.84
   if front and (j<2 or j>=5):continue
   aa=j*n+i;b=j*n+(i+1)%n;f.append((aa,b,b+n,aa+n))
 ob=mesh('Ref16_NotchedCalfArmor.'+side,v,f);thickness(ob,.006)
 # Two nested gold-lined recesses with seated black piston rods.
 link('Ref16_LowerShinActuator.'+side,p(.267,-.048,.195),p(.253,-.059,.289),.027,.031)
 link('Ref16_LowerShinRod.'+side,p(.266,-.068,.204),p(.255,-.078,.27),.011,.013,'Gold')
 link('Ref16_KneeActuator.'+side,p(.21,-.036,.478),p(.224,-.06,.409),.028,.032)
 link('Ref16_KneeRod.'+side,p(.215,-.057,.466),p(.224,-.078,.42),.012,.013,'Gold')
 panel('Ref16_KneeCap',[(.175,.579),(.213,.584),(.236,.557),(.218,.528),(.186,.529),(.17,.552)],-.095,.02)
 # Slim transverse seam follows the calf surface at mid-height.
 z,cx,cy,rx,ry=secs[3];pts=[]
 for i in range(25):
  a=-2.75+2.35*i/24;pts.append(p(cx+(rx+.001)*signed(math.cos(a),.62),cy+(ry+.001)*signed(math.sin(a),.62),z+.007*math.cos(a)))
 curve('Ref16_CalfPanelBreak.'+side,pts)
 # Gold inserts at the upper thigh follow its existing outer contour.
 panel('Ref16_ThighGold',[(.199,.694),(.225,.706),(.226,.674),(.205,.639),(.193,.645)],-.06,.009,'Gold')
 # Ankle housings taper into instep instead of exposed rectangular cuffs.
 old=bpy.data.objects.get('Target_AnkleInstep.'+side)
 if old:hide(old)
 H['loft']('Ref16_AnkleFork.'+side,[(.103,.121,.112,s*.28,.012),(.122,.115,.106,s*.28,.012),(.148,.09,.085,s*.279,.013)],C,M['Ivory'],bevel=.011)
# Remove stray floating hardware inherited from earlier experimental layers.
for o in visible:
 if o.name.startswith(('Armor_Bolt_1.314','Shoulder_CornerBolt','Shoulder_GoldCorner')):hide(o)
# Warm paint and restrained metallic contrast, shared across the model.
for key,color,metal,rough in [('Ivory',(.76,.69,.56,1),.12,.32),('Gold',(.60,.36,.10,1),.75,.27),('Frame',(.035,.043,.048,1),.64,.35)]:
 node=next(n for n in M[key].node_tree.nodes if n.type=='BSDF_PRINCIPLED');node.inputs['Base Color'].default_value=color;node.inputs['Metallic'].default_value=metal
for o in C.objects:
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(Path('D:\\codex+blender\\model\\blender\\history\\robot_reference_construction.blend')))
print('Saved reference construction pass:',len(C.objects),'new parts.')
