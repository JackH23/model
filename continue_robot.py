import bpy, math
from pathlib import Path
from mathutils import Vector
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH3_Armor_Details')
M=H['mats']()
def box(n,p,s,m='Ivory',b=.006): return H['box'](n,p,s,C,M[m],b)
def disc(n,p,r,d,m='Frame',a=(1,0,0)): return H['cylinder'](n,p,r,d,C,M[m],axis=a,bevel=.002)
def ring(n,p,r,ri,d,m='Gold',a=(1,0,0)): return H['ring'](n,p,r,ri,d,C,M[m],axis=a)
def panel(n,pts,y,d=.012,m='Ivory'): return H['prism_xz'](n,pts,y,d,C,M[m],bevel=.004)
def seam(n,pts,r=.0018,m='Frame'):
 cv=bpy.data.curves.new(n,'CURVE'); cv.dimensions='3D'; cv.bevel_depth=r; cv.bevel_resolution=2
 sp=cv.splines.new('POLY'); sp.points.add(len(pts)-1)
 for v,p in zip(sp.points,pts): v.co=(*p,1)
 ob=bpy.data.objects.new(n,cv); C.objects.link(ob); ob.parent=bpy.data.objects['Robot_Phase1']; cv.materials.append(M[m]); return ob
for sign,side in [(1,'L'),(-1,'R')]:
 def p(x,y,z): return (sign*x,y,z)
 def plate(n,pts,y,d=.012,m='Ivory'): return panel(n+'.'+side,[(sign*x,z) for x,z in pts],y,d,m)
 # Helmet cheek plates and brow layering.
 plate('Helmet_Cheek',[(.116,1.438),(.166,1.449),(.177,1.477),(.146,1.474)],-.174,.018,'Gold')
 plate('Helmet_Brow',[(.012,1.602),(.136,1.59),(.158,1.577),(.095,1.581),(.018,1.59)],-.183,.013)
 seam('Helmet_PanelSeam.'+side,[p(.115,-.149,1.64),p(.15,-.165,1.614),p(.174,-.161,1.594)])
 ring('Ear_OuterBezel.'+side,p(.251,.01,1.524),.086,.075,.008,'Ivory')
 ring('Ear_InnerBezel.'+side,p(.257,.01,1.524),.057,.051,.006,'Gold')
 disc('Ear_Center.'+side,p(.257,.01,1.524),.048,.006)
 for z in [1.50,1.548]: disc('Ear_Fastener_'+str(z)+'.'+side,p(.259,.071,z),.005,.006,'Gold')
 # Shoulder inset, cap overlays, hardware.
 plate('Shoulder_TopPlate',[(.264,1.325),(.35,1.351),(.421,1.325),(.438,1.297),(.406,1.303),(.35,1.329)],-.089,.02)
 plate('Shoulder_GoldCorner',[(.405,1.30),(.439,1.281),(.424,1.236),(.395,1.247)],-.118,.016,'Gold')
 disc('Shoulder_CornerBolt.'+side,p(.414,-.13,1.269),.011,.008,'Frame',(0,1,0))
 ring('Shoulder_HubRim.'+side,p(.477,.01,1.251),.065,.051,.012,'Gold')
 ring('Shoulder_HubInset.'+side,p(.485,.01,1.251),.046,.039,.009,'Frame')
 disc('Shoulder_HubCenter.'+side,p(.488,.01,1.251),.034,.008)
 # Layered front pectoral panels.
 plate('Chest_Collar',[(.025,1.289),(.127,1.281),(.177,1.247),(.156,1.234),(.089,1.257),(.033,1.262)],-.114,.022)
 plate('Chest_GoldLatch',[(.152,1.246),(.186,1.231),(.18,1.205),(.158,1.214)],-.137,.012,'Gold')
 seam('Chest_Seam.'+side,[p(.054,-.137,1.227),p(.118,-.145,1.208),p(.162,-.126,1.15),p(.116,-.124,1.084)])
 for z in [1.10,1.117,1.134]: box('Rib_Vent_'+str(z)+'.'+side,p(.17,-.105,z),(.031,.019,.006),'Frame',.002)
 plate('Forearm_FacePlate',[(.357,.963),(.398,1.005),(.449,.98),(.466,.91),(.428,.851),(.386,.868)],-.126,.014)
 plate('Forearm_GoldTip',[(.386,.88),(.429,.861),(.421,.838),(.386,.851)],-.13,.013,'Gold')
 seam('Forearm_Seam.'+side,[p(.367,-.136,.942),p(.407,-.139,.928),p(.445,-.134,.949)])
 ring('Elbow_Rim.'+side,p(.451,-.004,1.018),.049,.037,.009,'Gold')
 disc('Elbow_Axle.'+side,p(.458,-.004,1.018),.028,.011)
 # Hip and leg mechanical layering.
 ring('Hip_Rim.'+side,p(.269,.035,.82),.07,.054,.013,'Gold')
 disc('Hip_Axle.'+side,p(.279,.035,.82),.05,.012)
 ring('Hip_Status.'+side,p(.287,.035,.82),.036,.031,.006,'Cyan')
 plate('Thigh_FacePlate',[(.121,.784),(.185,.81),(.245,.763),(.239,.677),(.205,.637),(.151,.674)],-.122,.014)
 plate('Thigh_GoldEdge',[(.20,.652),(.237,.685),(.246,.652),(.223,.612),(.201,.621)],-.126,.014,'Gold')
 seam('Thigh_Seam.'+side,[p(.134,-.133,.739),p(.18,-.137,.721),p(.234,-.132,.731)])
 ring('Knee_OuterRim.'+side,p(.319,-.055,.54),.056,.042,.012,'Gold')
 disc('Knee_Hub.'+side,p(.328,-.055,.54),.037,.009)
 disc('Knee_Light.'+side,p(.335,-.055,.54),.016,.006,'Cyan')
 plate('Shin_FacePlate',[(.188,.431),(.23,.478),(.295,.459),(.324,.396),(.291,.276),(.25,.235),(.209,.294)],-.154,.014)
 seam('Shin_Seam.'+side,[p(.197,-.164,.38),p(.248,-.166,.357),p(.304,-.162,.377)])
 plate('Shin_GoldEdge',[(.291,.297),(.314,.348),(.326,.32),(.306,.253),(.282,.232)],-.129,.016,'Gold')
 box('Ankle_Status.'+side,p(.278,-.145,.214),(.035,.012,.017),'Cyan',.003)
 for dx in [-.064,0,.064]:
  box('Toe_Armor_'+str(dx)+'.'+side,p(.345+dx,-.231,.103),(.057,.10,.026),'Ivory',.008)
  box('Toe_Gold_'+str(dx)+'.'+side,p(.345+dx,-.279,.067),(.032,.012,.042),'Gold',.004)
 # Segmented finger armor and gold knuckles, preserving original hands.
 for idx,x in enumerate([.419,.449,.479,.51]):
  box('Knuckle_'+str(idx)+'.'+side,p(x,-.092,.721),(.021,.017,.019),'Gold',.004)
  for j,z in enumerate([.696,.674]): box('Finger_Phalanx_'+str(idx)+'_'+str(j)+'.'+side,p(x,-.108,z),(.018,.014,.016),'Frame',.003)
 for x,z,y in [(.35,1.314,-.108),(.396,.952,-.14),(.191,.773,-.135),(.245,.423,-.168)]:
  disc('Armor_Bolt_'+str(z)+'.'+side,p(x,y,z),.006,.004,'Gold',(0,1,0))
 # Rear shoulder vents and calf service plates.
 for i in range(3): box('Shoulder_RearVent_'+str(i)+'.'+side,p(.345,.138,1.23+i*.018),(.065,.008,.007),'Frame',.002)
 box('Calf_ServicePlate.'+side,p(.27,.091,.35),(.09,.026,.15),'Frame',.013)
 for i in range(4): box('Calf_Vent_'+str(i)+'.'+side,p(.27,.109,.31+i*.024),(.065,.008,.008),'Gold',.002)
box('Chin_Armor',(0,-.178,1.389),(.14,.031,.027),'Ivory',.008)
box('Belt_Center',(0,-.089,.916),(.10,.025,.043),'Frame',.008)
box('Belt_Indicator',(0,-.105,.919),(.049,.008,.011),'Cyan',.002)
for i in range(3): box('Abdomen_Rib_'+str(i),(0,-.071,.969+i*.023),(.16-i*.012,.027,.011),'Frame',.003)
box('Back_Reactor_Frame',(0,.215,1.193),(.108,.036,.151),'Frame',.014)
panel('Back_Reactor', [(-.032,1.22),(.032,1.22),(0,1.175)],.237,.009,'Cyan')
for x in [-.057,.057]: box('Back_GoldRail_'+str(x),(x,.216,1.17),(.012,.025,.18),'Gold',.003)
root=bpy.data.objects['Robot_Phase1']; root['scope']='Reference refinement: segmented armor, layered hubs, vents, fasteners and hand details'
bpy.context.scene['phase']='Reference armor refinement'
out=Path(r'D:\codex+blender\model')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'robot_reference_refined.blend'))
print('Saved refined robot; detail objects:',len(C.objects))
