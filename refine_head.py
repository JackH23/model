import bpy, math
from pathlib import Path
from mathutils import Vector
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH12_Reference_Head');M=H['mats']()
for o in list(C.objects):bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.objects:
 if o.name.startswith(('Head_','Helmet_','Ear_','Eye_','Antenna_','Chin_')):o.hide_render=True;o.hide_set(True)
def plate(n,pts,y,d=.02,m='Ivory',b=.005):return H['prism_xz'](n,pts,y,d,C,M[m],bevel=b)
def box(n,p,s,m='Frame',b=.005):return H['box'](n,p,s,C,M[m],b)
def cyl(n,p,r,d,m='Frame',a=(1,0,0)):return H['cylinder'](n,p,r,d,C,M[m],axis=a,bevel=.002,segments=64)
def ring(n,p,r,ri,d,m='Ivory'):return H['ring'](n,p,r,ri,d,C,M[m],axis=(1,0,0))
H['sphere']('RefHead_RearHelmet',(0,.035,1.515),(.386,.323,.294),C,M['Ivory'],segments=64,rings=32)
# Wide chamfered visor with a thick sculpted ivory surround.
outer=[(-.16,1.604),(-.088,1.64),(.085,1.64),(.164,1.605),(.187,1.565),(.178,1.461),(.126,1.402),(-.125,1.402),(-.18,1.461),(-.187,1.566)]
inner=[(-.139,1.578),(-.079,1.598),(.078,1.598),(.14,1.578),(.157,1.548),(.148,1.477),(.109,1.441),(-.108,1.441),(-.151,1.478),(-.159,1.548)]
verts=[(x,y,z) for y,poly in [(-.167,outer),(-.215,outer),(-.215,inner),(-.166,inner)] for x,z in poly];n=len(outer)
faces=[]
for i in range(n):
 k=(i+1)%n
 faces += [(i,k,n+k,n+i),(n+i,n+k,2*n+k,2*n+i),(2*n+i,2*n+k,3*n+k,3*n+i),(3*n+i,3*n+k,k,i)]
H['finish_mesh']('RefHead_VisorArmorFrame',verts,faces,C,M['Ivory'],bevel=.009)
plate('RefHead_VisorRubber',inner,-.19,.035,'Frame',.009)
plate('RefHead_VisorGlass',[(x*.96,1.52+(z-1.52)*.95) for x,z in inner],-.212,.011,'Visor',.009)
plate('RefHead_CrownInset',[(-.043,1.64),(.043,1.64),(.037,1.664),(-.037,1.664)],-.08,.104,'Frame',.005)
for sign,side in [(1,'L'),(-1,'R')]:
 def p(x,y,z):return(sign*x,y,z)
 def panel(n,pts,y,d=.015,m='Ivory',b=.005):return plate(n+'.'+side,[(sign*x,z) for x,z in pts],y,d,m,b)
 panel('RefHead_Brow',[(.006,1.614),(.086,1.623),(.149,1.591),(.158,1.568),(.111,1.589),(.015,1.596)],-.224,.019)
 panel('RefHead_CheekGold',[(.128,1.467),(.16,1.481),(.177,1.455),(.153,1.431),(.12,1.439)],-.225,.012,'Gold',.003)
 panel('RefHead_Jaw',[(.029,1.421),(.105,1.432),(.133,1.414),(.102,1.394),(.034,1.396)],-.205,.023)
 box('RefHead_Eye.'+side,p(.084,-.226,1.519),(.025,.012,.067),'Cyan',.011)
 # Layered circular ear bearing with a deep blue center and bright cyan annulus.
 cyl('RefHead_EarMount.'+side,p(.195,.022,1.529),.094,.047)
 cyl('RefHead_EarShell.'+side,p(.224,.022,1.529),.089,.042,'Ivory')
 ring('RefHead_EarGold.'+side,p(.249,.022,1.529),.083,.074,.008,'Gold')
 cyl('RefHead_EarInset.'+side,p(.253,.022,1.529),.073,.012,'Visor')
 ring('RefHead_EarLight.'+side,p(.261,.022,1.529),.067,.055,.007,'Cyan')
 cyl('RefHead_EarCenter.'+side,p(.265,.022,1.529),.049,.006,'Frame')
 # Swept antenna blade with a dark root and cyan inset.
 panel('RefHead_AntennaRoot',[(.119,1.635),(.151,1.628),(.182,1.681),(.159,1.697)],.025,.065,'Frame')
 panel('RefHead_Antenna',[(.145,1.65),(.17,1.657),(.227,1.77),(.222,1.788),(.2,1.772),(.153,1.709)],.024,.035,'Gold',.004)
 panel('RefHead_AntennaInset',[(.161,1.685),(.17,1.686),(.194,1.735),(.185,1.731)],.003,.005,'Frame',.002)
 panel('RefHead_AntennaLight',[(.167,1.696),(.172,1.696),(.179,1.713),(.174,1.712)],-.001,.005,'Cyan',.001)
 cyl('RefHead_TempleBolt.'+side,p(.172,-.197,1.577),.0045,.005,'Gold',(0,1,0))
box('RefHead_ChinInset',(0,-.221,1.412),(.049,.01,.014),'Frame',.004)
bpy.context.view_layer.update()
sc=bpy.context.scene;cam=sc.camera
cam.location=(.9,-1.8,1.78);cam.rotation_euler=(Vector((0,0,1.555))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.68
sc.render.resolution_x=1100;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\head_reference_detail.png';bpy.ops.render.render(write_still=True)
cam.location=(2.6,-4.5,2.5);cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2
sc.render.resolution_x=900;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\head_reference_full.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot_head_refined.blend')
print('Saved head refinement; previous head parts retained hidden, neck unchanged.')
