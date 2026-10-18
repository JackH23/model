import bpy, math
from pathlib import Path
from mathutils import Vector, Matrix
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH5_Reference_Hands'); M=H['mats']()
for ob in list(bpy.data.objects):
 if ob.name.startswith('Repair_') and 'Neck' not in ob.name:
  bpy.data.objects.remove(ob,do_unlink=True)
for sign,side in [(1,'L'),(-1,'R')]:
 pivot=bpy.data.objects['Hand_Assembly.'+side]
 T=Matrix.Translation(pivot.location)@Matrix.Rotation(math.radians(-sign*15),4,'Y')
 def place(ob):
  bpy.context.view_layer.update()
  world=T@ob.matrix_world.copy(); ob.parent=pivot; ob.matrix_world=world
  return ob
 def box(n,p,s,m='Frame',b=.004): return place(H['box'](n+'.'+side,p,s,C,M[m],b))
 def cyl(n,p,r,d,m='Frame',axis=(1,0,0)): return place(H['cylinder'](n+'.'+side,p,r,d,C,M[m],axis=axis,bevel=.0015))
 def link(n,a,b,w,d,m='Frame',bevel=.004):
  a,b=Vector(a),Vector(b)
  ob=H['box'](n+'.'+side,(a+b)/2,(w,d,(b-a).length+.003),C,M[m],bevel)
  ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
  return place(ob)
 cyl('Ref_Wrist',(0,0,-.009),.034,.043,axis=(0,0,1))
 box('Ref_PalmCore',(0,.002,-.066),(.104,.055,.081),b=.014)
 # Sculpted chamfered back-of-hand plate with lower finger recesses.
 outline=[(-.048,-.033),(.043,-.033),(.051,-.048),(.048,-.085),(.033,-.097),(-.042,-.095),(-.051,-.078)]
 plate=H['prism_xz']('Ref_HandArmor.'+side,[(sign*x,z) for x,z in outline],-.033,.019,C,M['Ivory'],bevel=.006)
 place(plate)
 box('Ref_WristGold',(0,-.036,-.029),(.067,.013,.009),'Gold',.003)
 for x in [-.035,.035]: cyl('Ref_ArmorBolt_'+str(x),(sign*x,-.045,-.08),.0045,.004,'Gold',(0,1,0))
 # Four fingers: knuckle, proximal, middle, tip along a curved chain.
 for i,(x,L,bend) in enumerate([(-.037,.073,0),(-.012,.080,5),(.013,.076,10),(.037,.062,15)]):
  x*=sign
  base=Vector((x,0,-.105))
  cyl('Ref_MCP_'+str(i),base,.010,.020)
  box('Ref_KnuckleGold_'+str(i),(x,-.027,-.101),(.017,.009,.010),'Gold',.0025)
  for j,(frac,angle) in enumerate(zip([.43,.33,.24],[12+bend,55+bend,100+bend])):
   theta=math.radians(angle)
   end=base+Vector((sign*.001*j,math.sin(theta)*L*frac,-math.cos(theta)*L*frac))
   width=.021 if i<3 else .018
   link('Ref_Finger_'+str(i)+'_'+str(j),base,end,width,.023,bevel=.005)
   # Raised graphite dorsal shell follows the finger direction.
   normal=Vector((0,-math.cos(theta),-math.sin(theta)))
   mid=(base+end)/2+normal*.012
   a=mid-(end-base)*.34; b=mid+(end-base)*.34
   link('Ref_Dorsal_'+str(i)+'_'+str(j),a,b,width*.85,.006,'Frame',.002)
   if j<2:
    cyl('Ref_Hinge_'+str(i)+'_'+str(j),end,.0095,width+.001)
    cyl('Ref_HingePin_'+str(i)+'_'+str(j),end+Vector((sign*(width/2+.0015),0,0)),.004,.002,'Gold')
   base=end
 # Opposition thumb: angled away from the palm, then curling inward.
 a=Vector((-sign*.047,.001,-.058)); b=Vector((-sign*.070,.009,-.083)); c=Vector((-sign*.073,.032,-.107)); d=Vector((-sign*.058,.049,-.12))
 cyl('Ref_ThumbSocket',a,.014,.025,axis=(0,1,0))
 for j,(start,end) in enumerate([(a,b),(b,c),(c,d)]):
  link('Ref_Thumb_'+str(j),start,end,.025-j*.002,.026,bevel=.006)
  if j<2: cyl('Ref_ThumbJoint_'+str(j),end,.010,.025,axis=(0,1,0))
 box('Ref_ThumbRootArmor',(-sign*.053,-.018,-.062),(.024,.014,.032),'Ivory',.005)
bpy.context.view_layer.update()
sc=bpy.context.scene;cam=sc.camera
cam.location=(.95,-1.8,1.03);cam.rotation_euler=(Vector((.47,-.02,.72))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.32
sc.render.resolution_x=1000;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\robot\renders\previews\reference_hand_closeup.png'
bpy.ops.render.render(write_still=True)
cam.location=(2.6,-4.5,2.5);cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2
sc.render.resolution_x=900;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\robot\renders\previews\reference_hands_full.png'
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot\blender\history\robot_reference_hands.blend')
print('Reference hands saved with connected curled digits and reduced knuckle hardware.')
