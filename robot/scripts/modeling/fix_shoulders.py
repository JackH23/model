import bpy, math
from pathlib import Path
from mathutils import Vector
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH6_Shoulder_Connections');M=H['mats']()
for ob in list(C.objects): bpy.data.objects.remove(ob,do_unlink=True)
for sign,side in [(1,'L'),(-1,'R')]:
 def cyl(n,x,r,d,m='Frame',z=1.235,y=.015,axis=(1,0,0)):
  return H['cylinder'](n+'.'+side,(sign*x,y,z),r,d,C,M[m],axis=axis,bevel=.003,segments=48)
 def ring(n,x,r,ri,d,m='Frame'):
  return H['ring'](n+'.'+side,(sign*x,.015,1.235),r,ri,d,C,M[m],axis=(1,0,0))
 # Continuous axle embeds in the torso and reaches the existing shoulder joint.
 cyl('Shoulder_Connector_Axle',.218,.071,.196)
 cyl('Shoulder_TorsoSocket',.173,.091,.052)
 ring('Shoulder_SocketLip',.202,.095,.073,.016)
 ring('Shoulder_GoldBearing',.213,.093,.079,.009,'Gold')
 cyl('Shoulder_BearingSleeve',.241,.081,.060)
 for i,x in enumerate([.222,.235,.248,.261]):
  ring('Shoulder_Bellows_'+str(i),x,.088,.074,.007)
 ring('Shoulder_ArmBearing',.276,.091,.074,.013)
 ring('Shoulder_ArmGoldTrim',.283,.089,.079,.006,'Gold')
 # Under-cap yoke joins the shoulder socket to the upper arm core.
 cyl('Shoulder_UpperArmYoke',.322,.059,.102,z=1.172,y=.014,axis=(0,0,1))
 for i,angle in enumerate([45,135,225,315]):
  a=math.radians(angle)
  H['cylinder']('Shoulder_SocketBolt_'+str(i)+'.'+side,(sign*.211,.015+.084*math.cos(a),1.235+.084*math.sin(a)),.004,.006,C,M['Gold'],axis=(1,0,0),bevel=.001)
bpy.context.view_layer.update()
bpy.data.objects['Robot_Phase1']['shoulder_connection']='Continuous torso-embedded axle, layered bearing socket and upper arm yoke on both sides.'
sc=bpy.context.scene;cam=sc.camera
cam.location=(.85,-1.8,1.48);cam.rotation_euler=(Vector((.225,.005,1.235))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.54
sc.render.resolution_x=1000;sc.render.resolution_y=900
sc.render.filepath=r'D:\codex+blender\model\robot\renders\previews\shoulder_fixed_detail.png';bpy.ops.render.render(write_still=True)
cam.location=(2.6,-4.5,2.5);cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2
sc.render.resolution_x=900;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\robot\renders\previews\shoulders_fixed_full.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot\blender\history\robot_shoulders_connected.blend')
print('Saved both shoulder connections; axle spans |X| 0.120 to 0.316 m, overlapping torso and shoulder joint.')
