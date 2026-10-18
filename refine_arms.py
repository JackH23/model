import bpy, math
from pathlib import Path
from mathutils import Vector
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH8_Reference_ArmArmor');M=H['mats']()
for ob in list(C.objects): bpy.data.objects.remove(ob,do_unlink=True)
for ob in bpy.data.objects:
 if ob.name.startswith(('Shoulder_Cap_Block','Shoulder_TopPlate','Shoulder_GoldCorner','Shoulder_CornerBolt','Shoulder_RearVent','UpperArm_Block','Forearm_Block','Forearm_FacePlate','Forearm_Seam','Forearm_GoldTip','Armor_Bolt_0.952')):
  ob.hide_render=True;ob.hide_set(True)
for sign,side in [(1,'L'),(-1,'R')]:
 def p(x,y,z): return (sign*x,y,z)
 def box(n,loc,size,m='Ivory',b=.005): return H['box'](n+'.'+side,p(*loc),size,C,M[m],b)
 def panel(n,pts,y,d=.013,m='Ivory'): return H['prism_xz'](n+'.'+side,[(sign*x,z) for x,z in pts],y,d,C,M[m],bevel=.005)
 def cyl(n,loc,r,d,m='Frame',axis=(1,0,0)):return H['cylinder'](n+'.'+side,p(*loc),r,d,C,M[m],axis=axis,bevel=.002)
 def link(n,a,b,w,d,m='Frame'):return H['segment_box'](n+'.'+side,p(*a),p(*b),w,d,C,M[m],bevel=.005)
 # A rounded cap split into six curved armor sectors with narrow seams.
 for k in range(6):
  verts=[];faces=[];nu=8;nv=10
  for j in range(nv+1):
   phi=.055+(1.84-.055)*j/nv
   for i in range(nu+1):
    theta=2*math.pi*(k+i/nu)/6+.010*(1-2*i/nu)
    verts.append(p(.34+.126*math.sin(phi)*math.cos(theta),.012+.126*math.sin(phi)*math.sin(theta),1.255+.108*math.cos(phi)))
  for j in range(nv):
   for i in range(nu):
    a=j*(nu+1)+i;faces.append((a,a+1,a+nu+2,a+nu+1))
  ob=H['finish_mesh']('Arm_RoundedShoulder_'+str(k)+'.'+side,verts,faces,C,M['Ivory'],smooth=True)
  mod=H['modifier'](ob,'Armor shell thickness','SOLIDIFY');mod.thickness=.007
 panel('Arm_ShoulderGold',[(.397,1.252),(.444,1.258),(.456,1.227),(.436,1.211),(.406,1.222)],-.097,.017,'Gold')
 cyl('Arm_ShoulderBolt',(.432,-.112,1.236),.010,.007,'Frame',(0,1,0))
 # Narrow biceps armor leaves the dark armature and side actuators exposed.
 panel('Arm_BicepShell',[(.319,1.195),(.364,1.197),(.39,1.154),(.375,1.099),(.343,1.079),(.316,1.106)],-.072,.029)
 panel('Arm_BicepInset',[(.331,1.181),(.352,1.184),(.369,1.15),(.356,1.118),(.337,1.126)],-.091,.008,'Frame')
 link('Arm_BicepPiston',(.389,.016,1.19),(.415,.012,1.056),.027,.033)
 link('Arm_BicepPistonRod',(.399,-.013,1.146),(.415,-.017,1.057),.013,.015,'Gold')
 cyl('Arm_BicepPivot',(.406,.012,1.08),.022,.034)
 # Multi-section tapered gauntlet with a split front face and wrist notch.
 H['loft']('Arm_ForearmShell.'+side,[(.842,.089,.103,sign*.449,-.036),(.88,.132,.146,sign*.433,-.035),(.96,.149,.156,sign*.402,-.027),(.995,.11,.13,sign*.393,-.018)],C,M['Ivory'],bevel=.013)
 panel('Arm_ForearmOuterPanel',[(.404,.986),(.458,.959),(.48,.904),(.445,.868),(.419,.895),(.43,.936)],-.111,.013)
 panel('Arm_ForearmInnerPanel',[(.369,.971),(.397,.983),(.419,.943),(.406,.905),(.43,.869),(.399,.861),(.364,.914)],-.113,.012)
 panel('Arm_ForearmGoldCuff',[(.399,.876),(.442,.858),(.46,.875),(.454,.844),(.423,.83),(.398,.847)],-.097,.019,'Gold')
 box('Arm_ForearmVent',(.412,-.116,.913),(.037,.013,.017),'Frame',.002)
 box('Arm_ForearmStatus',(.411,-.124,.916),(.022,.005,.006),'Cyan',.001)
 for z,x in [(.966,.389),(.886,.461)]: cyl('Arm_ForearmBolt_'+str(z),(x,-.124,z),.0045,.005,'Gold',(0,1,0))
bpy.context.view_layer.update()
sc=bpy.context.scene;cam=sc.camera
cam.location=(1.05,-1.8,1.36);cam.rotation_euler=(Vector((.36,0,1.09))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.69
sc.render.resolution_x=900;sc.render.resolution_y=1100
sc.render.filepath=r'D:\codex+blender\model\arms_reference_detail.png';bpy.ops.render.render(write_still=True)
cam.location=(2.6,-4.5,2.5);cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2
sc.render.resolution_x=900;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\arms_reference_full.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot_arms_refined.blend')
print('Saved rounded shoulder caps, exposed biceps mechanisms and segmented tapered forearms on both sides.')
