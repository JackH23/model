import bpy, math
from pathlib import Path
from mathutils import Vector
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH9_Reference_Torso');M=H['mats']()
for ob in list(C.objects): bpy.data.objects.remove(ob,do_unlink=True)
for ob in bpy.data.objects:
 if ob.name.startswith(('Chest_','Rib_Vent','Abdomen_Rib')) or ob.name=='Torso_Chest_Block':
  ob.hide_render=True;ob.hide_set(True)
def box(n,p,s,m='Frame',b=.005):return H['box'](n,p,s,C,M[m],b)
def plate(n,pts,y,d=.02,m='Ivory',b=.006):return H['prism_xz'](n,pts,y,d,C,M[m],bevel=b)
def cyl(n,p,r,d,m='Frame',axis=(0,1,0)):return H['cylinder'](n,p,r,d,C,M[m],axis=axis,bevel=.002)
# Compact dark inner thorax supports a set of independently editable armor plates.
H['loft']('Torso_ArmoredChassis',[(1.03,.22,.18,0,.027),(1.15,.35,.24,0,.022),(1.255,.395,.235,0,.025),(1.292,.24,.18,0,.025)],C,M['Frame'],bevel=.018)
# Collar around neck, supported by the thorax instead of loose top decorations.
H['loft']('Torso_CollarShell',[(1.254,.30,.19,0,.02),(1.28,.27,.20,0,.02),(1.301,.20,.17,0,.02)],C,M['Ivory'],bevel=.009)
for sign,side in [(1,'L'),(-1,'R')]:
 def p(x,y,z):return (sign*x,y,z)
 def panel(n,pts,y,d=.02,m='Ivory',b=.006):return plate(n+'.'+side,[(sign*x,z) for x,z in pts],y,d,m,b)
 # Swept pectoral armor wraps the reactor and tapers to the sternum.
 panel('Torso_Pectoral',[(.012,1.268),(.094,1.288),(.173,1.263),(.206,1.225),(.178,1.179),(.128,1.154),(.096,1.191),(.066,1.235)],-.117,.045)
 panel('Torso_LowerChest',[(.185,1.187),(.161,1.124),(.101,1.066),(.043,1.043),(.022,1.083),(.059,1.124),(.098,1.153),(.124,1.142)],-.113,.036)
 panel('Torso_SideArmor',[(.185,1.239),(.22,1.216),(.208,1.164),(.177,1.128),(.171,1.185)],-.057,.10)
 panel('Torso_GoldCollar',[(.122,1.28),(.161,1.27),(.178,1.252),(.144,1.253),(.119,1.264)],-.145,.012,'Gold',.003)
 panel('Torso_GoldRib',[(.167,1.146),(.184,1.168),(.191,1.143),(.165,1.11),(.148,1.113)],-.127,.013,'Gold',.003)
 cyl('Torso_PectoralBolt.'+side,p(.176,-.145,1.232),.005,.006,'Gold')
 cyl('Torso_LowerBolt.'+side,p(.1,-.138,1.092),.004,.006,'Gold')
 # Visible side rib mechanics with brass piston rods, tucked behind armor edges.
 for i in range(3):box('Torso_RibVent_'+str(i)+'.'+side,p(.177,.001,1.104+i*.023),(.048,.13,.011),'Frame',.003)
 a=Vector(p(.137,-.038,1.107));b=Vector(p(.108,-.042,1.019))
 H['segment_box']('Torso_SideActuator.'+side,a,b,.026,.031,C,M['Frame'],bevel=.006)
 H['segment_box']('Torso_SidePiston.'+side,a+Vector((0,-.019,0)),b+Vector((0,-.019,0)),.010,.011,C,M['Gold'],bevel=.003)
# Layered triangular bezel: the cyan core sits behind a raised metallic lip.
tri=[(-.076,1.244),(.076,1.244),(0,1.109)]
plate('Torso_ReactorSocket',tri,-.143,.044,'Frame',.007)
plate('Torso_ReactorMetalBezel',[(-.066,1.234),(.066,1.234),(0,1.119)],-.168,.013,'Visor',.004)
plate('Torso_ReactorGlass',[(-.05,1.224),(.05,1.224),(0,1.137)],-.176,.007,'Cyan',.004)
# Thin inner triangular border around the light.
for i,(a,b) in enumerate(zip([(-.059,-.182,1.23),(.059,-.182,1.23),(0,-.182,1.126)],[ (.059,-.182,1.23),(0,-.182,1.126),(-.059,-.182,1.23)])):
 H['segment_box']('Torso_ReactorLip_'+str(i),a,b,.006,.006,C,M['Frame'],bevel=.002)
plate('Torso_SternumTip',[(-.043,1.083),(.043,1.083),(.031,1.043),(0,1.024),(-.031,1.043)],-.107,.026)
box('Torso_SternumFastener',(0,-.124,1.053),(.016,.008,.013),'Gold',.002)
# Narrow segmented abdomen rather than the broad cylindrical blockout.
waist=bpy.data.objects['Waist_Joint'];waist.scale.x*=.82;waist.scale.y*=.86
for i,z in enumerate([.956,.982,1.008]):
 box('Torso_AbdominalVertebra_'+str(i),(0,-.061,z),(.116+i*.009,.036,.02),'Frame',.007)
 box('Torso_AbdominalInset_'+str(i),(0,-.082,z),(.065,.009,.007),'Visor',.002)
bpy.context.view_layer.update()
sc=bpy.context.scene;cam=sc.camera
cam.location=(.7,-2,1.5);cam.rotation_euler=(Vector((0,0,1.15))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.66
sc.render.resolution_x=1100;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\torso_reference_detail.png';bpy.ops.render.render(write_still=True)
cam.location=(2.6,-4.5,2.5);cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2
sc.render.resolution_x=900;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\torso_reference_full.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot_torso_refined.blend')
print('Saved layered torso, inset reactor, gold collar inserts, exposed side pistons and segmented abdomen.')
