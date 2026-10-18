import bpy, math
from pathlib import Path
from mathutils import Vector
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH11_LeftLeg_ShapePreview'); M=H['mats']()
for ob in list(C.objects): bpy.data.objects.remove(ob,do_unlink=True)
# One side only, retaining the other leg for comparison.
for ob in bpy.data.objects:
 if not ob.name.endswith('.L'): continue
 if ob.name.startswith(('Shin_','Foot_','Toe_','Calf_','Ankle_','Knee_','Leg_Shin','Leg_Calf','Leg_Ankle','Leg_KneeGuard','Leg_KneeInset')):
  ob.hide_render=True;ob.hide_set(True)
def mesh(n,v,f,m='Ivory',bevel=0):return H['finish_mesh'](n+'.L',v,f,C,M[m],bevel=bevel,smooth=True)
def cyl(n,p,r,d,m='Frame',axis=(1,0,0)):return H['cylinder'](n+'.L',p,r,d,C,M[m],axis=axis,bevel=.002,segments=48)
def seam(n,pts,m='Frame',r=.0012):
 cv=bpy.data.curves.new(n,'CURVE');cv.dimensions='3D';cv.bevel_depth=r;cv.bevel_resolution=3
 sp=cv.splines.new('POLY');sp.points.add(len(pts)-1)
 for q,p in zip(sp.points,pts):q.co=(*p,1)
 ob=bpy.data.objects.new(n+'.L',cv);C.objects.link(ob);ob.parent=bpy.data.objects['Robot_Phase1'];cv.materials.append(M[m])
# Smaller knee and continuous tapered calf: cross-sections are ellipses, not slabs.
H['sphere']('Preview_KneeBall.L',(.235,-.035,.54),(.129,.125,.125),C,M['Frame'],segments=40,rings=24)
cyl('Preview_KneeBearing',(.301,-.035,.54),.047,.014)
H['ring']('Preview_KneeTrim.L',(.31,-.035,.54),.042,.034,.006,C,M['Gold'],axis=(1,0,0))
cyl('Preview_KneeCenter',(.315,-.035,.54),.027,.007)
cyl('Preview_KneeLight',(.32,-.035,.54),.011,.004,'Cyan')
sections=[(.192,.307,.012,.044,.049),(.218,.302,.014,.049,.058),(.27,.291,.012,.06,.075),(.335,.278,.014,.079,.091),(.4,.262,.015,.087,.097),(.447,.25,.011,.081,.091),(.479,.243,.003,.065,.075),(.496,.24,-.004,.05,.059)]
for k in range(4):
 verts=[];faces=[];n=16
 for z,cx,cy,rx,ry in sections:
  for i in range(n+1):
   th=2*math.pi*(k+i/n)/4+.006*(1-2*i/n)
   verts.append((cx+rx*math.cos(th),cy+ry*math.sin(th),z))
 for j in range(len(sections)-1):
  for i in range(n):
   a=j*(n+1)+i;faces.append((a,a+1,a+n+2,a+n+1))
 ob=mesh('Preview_CalfShell_'+str(k),verts,faces)
 sol=H['modifier'](ob,'Calf armor thickness','SOLIDIFY');sol.thickness=.006
 sub=H['modifier'](ob,'Smooth calf contour','SUBSURF');sub.levels=2
# Central structure is enclosed by the calf, with short exposed ends.
H['segment_box']('Preview_ShinInner.L',(.24,.015,.497),(.307,.016,.17),.065,.073,C,M['Frame'],bevel=.015)
cyl('Preview_AnkleSocket',(.307,.013,.163),.041,.092,axis=(1,0,0))
cyl('Preview_AnkleCap',(.355,.013,.163),.032,.012)
H['ring']('Preview_AnkleTrim.L',(.363,.013,.163),.028,.022,.005,C,M['Gold'],axis=(1,0,0))
# Foot sole follows a rounded compact footprint rather than a rectangular platform.
outline=[(-.071,-.18),(.061,-.18),(.09,-.155),(.096,-.09),(.087,.035),(.065,.084),(-.065,.084),(-.087,.053),(-.099,-.07),(-.094,-.144)]
verts=[(.312+x,y,z) for z in [.004,.032] for x,y in outline];N=len(outline)
faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
mesh('Preview_RoundedSole',verts,faces,'Frame',.009)
# Continuous arched wedge from toe to heel; ankle settles inside its raised rear.
footsecs=[(-.176,.066,.069),(-.158,.085,.079),(-.105,.093,.094),(-.05,.091,.121),(.003,.083,.15),(.045,.074,.137),(.076,.057,.097)]
verts=[];faces=[];n=20
for y,w,top in footsecs:
 for i in range(n+1):
  a=math.pi*i/n
  verts.append((.312-w*math.cos(a),y,.031+(top-.031)*math.sin(a)**.62))
for j in range(len(footsecs)-1):
 for i in range(n):
  a=j*(n+1)+i;faces.append((a,a+1,a+n+2,a+n+1))
faces += [tuple(reversed(range(n+1))),tuple(range((len(footsecs)-1)*(n+1),len(footsecs)*(n+1)))]
ob=mesh('Preview_IntegratedFootShell',verts,faces)
sol=H['modifier'](ob,'Foot shell thickness','SOLIDIFY');sol.thickness=.007
sub=H['modifier'](ob,'Foot contour smoothing','SUBSURF');sub.levels=2
# Two shallow toe seams follow the arched surface rather than separate blocks.
for dx in [-.03,.03]:
 pts=[]
 for y,w,top in footsecs[:3]:
  a=math.acos(-dx/w);pts.append((.312+dx,y,.033+(top-.031)*math.sin(a)**.62))
 seam('Preview_ToeSeam_'+str(dx),pts)
# Restrained gold detail follows the fitted calf surface.
pts=[]
for z,cx,cy,rx,ry in sections[1:6]:
 th=-.55;pts.append((cx+(rx+.002)*math.cos(th),cy+(ry+.002)*math.sin(th),z))
seam('Preview_CalfGoldInset',pts,'Gold',.003)
bpy.context.view_layer.update()
sc=bpy.context.scene;cam=sc.camera
def render(name,eye,target,scale,x=900,y=1100):
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 sc.render.resolution_x=x;sc.render.resolution_y=y;sc.render.filepath=str(Path(r'D:\codex+blender\model')/name);bpy.ops.render.render(write_still=True)
render('leg_preview_side.png',(2,.015,.52),(.275,0,.36),.79)
render('leg_preview_threequarter.png',(1.1,-1.8,.86),(.275,-.015,.37),.84)
render('leg_preview_comparison.png',(0,-3,1.02),(0,0,.42),1.08,1100,1000)
cam.location=(2.6,-4.5,2.5);cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot_leg_shape_preview.blend')
print('Saved left-leg silhouette preview. Right leg and all earlier geometry preserved for comparison.')
