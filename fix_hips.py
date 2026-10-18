import bpy, math
from pathlib import Path
from mathutils import Vector
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH7_Hip_Connections');M=H['mats']()
for ob in list(C.objects): bpy.data.objects.remove(ob,do_unlink=True)
for n in ['Pelvis_Main_Block','Pelvis_OuterHip_Block.L','Pelvis_OuterHip_Block.R']:
 ob=bpy.data.objects.get(n)
 if ob: ob.hide_render=True; ob.hide_set(True)
def box(n,p,s,m='Frame',b=.008): return H['box'](n,p,s,C,M[m],b)
def cyl(n,p,r,d,m='Frame',axis=(1,0,0)): return H['cylinder'](n,p,r,d,C,M[m],axis=axis,bevel=.003,segments=48)
def plate(n,pts,y,d=.018,m='Ivory'): return H['prism_xz'](n,pts,y,d,C,M[m],bevel=.006)
# Pelvic chassis connects waist, hip bearings and the center shield.
box('Pelvis_InternalChassis',(0,.033,.864),(.158,.14,.132),b=.019)
cyl('Pelvis_WaistCoupler',(0,.035,.926),.072,.065,axis=(0,0,1))
cyl('Pelvis_ContinuousHipAxle',(0,.035,.846),.057,.405)
plate('Pelvis_ShieldBacking',[(-.071,.906),(.071,.906),(.062,.812),(.037,.751),(-.037,.751),(-.062,.812)],-.082,.027,'Frame')
plate('Pelvis_CenterShield',[(-.052,.871),(.052,.871),(.046,.802),(.025,.762),(-.025,.762),(-.046,.802)],-.103,.019)
plate('Pelvis_ShieldUpperInset',[(-.05,.898),(.05,.898),(.04,.871),(-.04,.871)],-.104,.012,'Frame')
plate('Pelvis_ShieldGoldTip',[(-.024,.78),(.024,.78),(.018,.76),(-.018,.76)],-.113,.008,'Gold')
for sign,side in [(1,'L'),(-1,'R')]:
 def ring(n,x,r,ri,d,m='Frame'):
  return H['ring'](n+'.'+side,(sign*x,.035,.846),r,ri,d,C,M[m],axis=(1,0,0))
 cyl('Hip_InnerSocket.'+side,(sign*.104,.035,.846),.076,.055)
 ring('Hip_InnerGoldBearing',.132,.079,.064,.008,'Gold')
 for i,x in enumerate([.143,.155,.167]): ring('Hip_BearingRib_'+str(i),x,.075,.061,.007)
 # Lower yoke embeds in existing thigh core while keeping joint visible above armor.
 cyl('Hip_ThighYoke.'+side,(sign*.183,.025,.801),.059,.110,axis=(0,0,1))
 # Angled side armor and gold inserts echo the reference's raised hip corners.
 pts=[(.148,.887),(.185,.899),(.223,.866),(.236,.811),(.214,.794),(.19,.826),(.175,.863)]
 plate('Hip_UpperArmor.'+side,[(sign*x,z) for x,z in pts],-.045,.027)
 pts=[(.181,.893),(.198,.883),(.218,.849),(.209,.834),(.19,.859)]
 plate('Hip_GoldInset.'+side,[(sign*x,z) for x,z in pts],-.062,.012,'Gold')
 # Diagonal dark brace from the pelvic core to each hip socket.
 a=Vector((sign*.053,-.025,.918));b=Vector((sign*.131,-.025,.86))
 ob=box('Pelvis_DiagonalBrace.'+side,(a+b)/2,(.028,.04,(b-a).length+.02),b=.009)
 ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
 cyl('Hip_BraceBolt.'+side,(sign*.108,-.05,.877),.008,.008,'Gold',axis=(0,1,0))
bpy.context.view_layer.update()
bpy.data.objects['Robot_Phase1']['hip_refinement']='Narrow tapered shield, exposed transverse hip axle, paired bearing sockets, thigh yokes and gold hip inserts.'
sc=bpy.context.scene;cam=sc.camera
cam.location=(.65,-1.8,1.02);cam.rotation_euler=(Vector((0,.015,.855))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.68
sc.render.resolution_x=1100;sc.render.resolution_y=850
sc.render.filepath=r'D:\codex+blender\model\hip_connections_detail.png';bpy.ops.render.render(write_still=True)
cam.location=(2.6,-4.5,2.5);cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2
sc.render.resolution_x=900;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\hip_connections_full.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot_hips_connected.blend')
print('Saved hip refinement; original pelvis blockouts retained hidden. Continuous hip axle connects both thigh yokes through chassis.')
