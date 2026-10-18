import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH4_Connection_Repairs'); M=H['mats']()
for old in list(C.objects): bpy.data.objects.remove(old,do_unlink=True)
root=bpy.data.objects['Robot_Phase1']
def box(n,p,s,m='Frame',b=.004): return H['box'](n,p,s,C,M[m],b)
def cyl(n,p,r,d,m='Frame',axis=(0,0,1)): return H['cylinder'](n,p,r,d,C,M[m],axis=axis,bevel=.003)
def ring(n,p,r,ri,d,m='Gold',axis=(0,0,1)): return H['ring'](n,p,r,ri,d,C,M[m],axis=axis)
def center(o): return sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
# Replace the inconsistent curved finger blockouts and their detached overlays.
prefix=('Hand_','Finger_','Thumb_','Knuckle_')
for o in list(bpy.data.objects):
 if o.name.startswith(prefix): bpy.data.objects.remove(o,do_unlink=True)
for sign,side in [(1,'L'),(-1,'R')]:
 wrist=Vector((sign*.452,-.038,.819))
 # Local negative Z follows the forearm toward the fingers.
 rot=Matrix.Rotation(math.radians(-sign*15),4,'Y')
 built=[]
 def add(ob):
  bpy.context.view_layer.update()
  ob.matrix_world=Matrix.Translation(wrist)@rot@ob.matrix_world
  built.append(ob); return ob
 add(cyl('Repair_WristSocket.'+side,(0,0,-.008),.039,.038))
 add(ring('Repair_WristTrim.'+side,(0,0,-.023),.041,.035,.009))
 add(box('Repair_Palm.'+side,(0,0,-.066),(.116,.067,.088),b=.012))
 add(box('Repair_HandArmor.'+side,(0,-.038,-.061),(.105,.018,.067),'Ivory',.008))
 for idx,(x,length) in enumerate([(-.043,.067),(-.014,.078),(.015,.073),(.044,.059)]):
  x*=sign
  z=-.105
  add(cyl('Repair_KnuckleJoint_'+str(idx)+'.'+side,(x,0,z),.012,.024,axis=(1,0,0)))
  add(box('Repair_KnuckleCap_'+str(idx)+'.'+side,(x,-.032,z),(.023,.014,.020),'Gold'))
  # Each section joins its predecessor; a small rearward bend relaxes the hand.
  for j,frac in enumerate([.38,.34,.28]):
   seg=length*frac
   yy=j*.006
   add(box('Repair_Finger_'+str(idx)+'_'+str(j)+'.'+side,(x,yy,z-seg/2),(.022,.029,seg+.005),b=.005))
   add(box('Repair_FingerPlate_'+str(idx)+'_'+str(j)+'.'+side,(x,yy-.017,z-seg/2),(.018,.008,max(.010,seg-.006)),'Frame',.002))
   z-=seg
   if j<2: add(cyl('Repair_FingerHinge_'+str(idx)+'_'+str(j)+'.'+side,(x,yy+.003,z),.011,.023,'Gold',axis=(1,0,0)))
 # Thumb anchored on the inner side of the palm, with two connected segments.
 add(cyl('Repair_ThumbRoot.'+side,(-sign*.055,0,-.065),.018,.026,axis=(0,1,0)))
 def link(n,a,b,width):
  a,b=Vector(a),Vector(b); ob=box(n,tuple((a+b)/2),(width,.031,(b-a).length+.008),b=.006)
  ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler(); return add(ob)
 a=(-sign*.055,0,-.065); b=(-sign*.078,-.006,-.091); c=(-sign*.068,-.012,-.119)
 link('Repair_ThumbProximal.'+side,a,b,.027)
 add(cyl('Repair_ThumbHinge.'+side,b,.014,.031,'Gold',axis=(0,1,0)))
 link('Repair_ThumbTip.'+side,b,c,.025)
 # Parent the complete assembly to a wrist pivot without shifting its geometry.
 pivot=bpy.data.objects.new('Hand_Assembly.'+side,None); C.objects.link(pivot); pivot.parent=root; pivot.location=wrist
 bpy.context.view_layer.update()
 for ob in built:
  world=ob.matrix_world.copy(); ob.parent=pivot; ob.matrix_world=world
# Extend the central neck into the helmet, retaining the head silhouette.
neck=bpy.data.objects['Neck_Joint']
pts=[neck.matrix_world@Vector(v) for v in neck.bound_box]
low=min(p.z for p in pts); high=max(p.z for p in pts)
for v in neck.data.vertices:
 w=neck.matrix_world@v.co
 w.z=low+(w.z-low)*(1.38-low)/(high-low)
 v.co=neck.matrix_world.inverted()@w
cyl('Repair_NeckUpperSocket',(0,.02,1.364),.079,.035)
ring('Repair_NeckUpperTrim',(0,.02,1.352),.081,.069,.008,'Gold')
cyl('Repair_NeckBaseCollar',(0,.02,1.303),.089,.020)
ring('Repair_NeckBaseArmor',(0,.02,1.309),.095,.074,.014,'Ivory')
bpy.context.view_layer.update()
root['connection_repairs']='Connected segmented hands aligned 15 degrees with forearms; neck reaches 1.380 m into helmet socket.'
out=Path(r'D:\codex+blender\model')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'robot_connections_fixed.blend'))
print('Saved corrected model. Neck top 1.380 m; helmet bottom 1.3602 m; overlap 19.8 mm. Connected hand assemblies:',len(C.objects))

