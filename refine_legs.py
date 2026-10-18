import bpy, math
from pathlib import Path
from mathutils import Vector
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH10_Reference_LegsFeet');M=H['mats']()
for ob in list(C.objects):bpy.data.objects.remove(ob,do_unlink=True)
for ob in bpy.data.objects:
 if ob.name.startswith(('Thigh_Block','Thigh_Face','Thigh_Gold','Thigh_Seam','Shin_Block','Shin_Core','Shin_Face','Shin_Gold','Shin_Seam','Foot_','Toe_','Knee_Cap','Ankle_Status','Calf_','Armor_Bolt_0.773','Armor_Bolt_0.423')):
  ob.hide_render=True;ob.hide_set(True)
for sign,side in [(1,'L'),(-1,'R')]:
 def p(x,y,z):return(sign*x,y,z)
 def box(n,loc,s,m='Frame',b=.006):return H['box'](n+'.'+side,p(*loc),s,C,M[m],b)
 def panel(n,pts,y,d=.018,m='Ivory'):return H['prism_xz'](n+'.'+side,[(sign*x,z) for x,z in pts],y,d,C,M[m],bevel=.006)
 def cyl(n,loc,r,d,m='Frame',axis=(1,0,0)):return H['cylinder'](n+'.'+side,p(*loc),r,d,C,M[m],axis=axis,bevel=.002)
 def link(n,a,b,w,d,m='Frame'):return H['segment_box'](n+'.'+side,p(*a),p(*b),w,d,C,M[m],bevel=.006)
 # Contoured thigh jacket with visible knee clearance and an angled armor edge.
 H['loft']('Leg_ThighShell.'+side,[(.625,.112,.147,sign*.22,.007),(.685,.176,.20,sign*.195,.018),(.769,.181,.209,sign*.178,.026),(.803,.127,.158,sign*.168,.032)],C,M['Ivory'],bevel=.017)
 panel('Leg_ThighOuter',[(.188,.794),(.245,.761),(.273,.691),(.243,.642),(.215,.655),(.221,.712),(.18,.755)],-.097,.023)
 panel('Leg_ThighInner',[(.125,.771),(.174,.786),(.202,.752),(.21,.705),(.187,.667),(.148,.691),(.119,.743)],-.101,.017)
 panel('Leg_KneeRecess',[(.191,.67),(.235,.676),(.251,.635),(.226,.6),(.199,.615)],-.096,.023,'Frame')
 panel('Leg_ThighGold',[(.235,.669),(.26,.689),(.259,.649),(.233,.615),(.217,.619)],-.115,.012,'Gold')
 cyl('Leg_ThighBolt',(.151,-.117,.75),.0045,.005,'Gold',(0,1,0))
 # Small floating knee guard backed by the existing hinge, rather than a large block.
 panel('Leg_KneeGuard',[(.205,.582),(.25,.583),(.269,.552),(.252,.523),(.216,.519),(.197,.548)],-.13,.019)
 panel('Leg_KneeInset',[(.213,.574),(.245,.575),(.252,.558),(.219,.55)],-.144,.007,'Gold')
 # Mechanical shin strut and paired actuators connect knee to ankle.
 link('Leg_ShinSpine',(.243,.016,.493),(.302,.018,.155),.075,.09)
 link('Leg_CalfActuator',(.293,.055,.465),(.337,.056,.206),.033,.039)
 link('Leg_CalfRod',(.308,.028,.379),(.34,.031,.205),.014,.017,'Gold')
 H['loft']('Leg_CalfRearShell.'+side,[(.232,.09,.10,sign*.305,.045),(.34,.14,.13,sign*.285,.053),(.45,.12,.106,sign*.263,.042)],C,M['Ivory'],bevel=.014)
 # Shin front splits into two sweeping surfaces, exposing a dark ankle notch.
 panel('Leg_ShinFront',[(.211,.474),(.251,.487),(.282,.458),(.301,.397),(.279,.327),(.284,.26),(.255,.225),(.227,.273),(.224,.34),(.192,.417)],-.108,.043)
 panel('Leg_ShinOuter',[(.286,.45),(.316,.416),(.336,.351),(.326,.28),(.303,.227),(.281,.26),(.289,.331),(.31,.385)],-.068,.035)
 panel('Leg_ShinGoldRail',[(.31,.393),(.327,.363),(.318,.299),(.296,.26),(.285,.269),(.303,.323)],-.097,.011,'Gold')
 box('Leg_AnkleRecess',(.281,-.093,.232),(.056,.032,.044),'Frame',.004)
 box('Leg_AnkleLight',(.281,-.112,.235),(.03,.007,.014),'Cyan',.002)
 cyl('Leg_ShinBolt',(.239,-.134,.443),.0045,.006,'Gold',(0,1,0))
 # Lateral ankle bearing ties shin into the heel fork.
 cyl('Leg_AnkleBearing',(.361,.016,.146),.043,.026)
 H['ring']('Leg_AnkleRim.'+side,p(.377,.016,.146),.036,.026,.007,C,M['Gold'],axis=(1,0,0))
 cyl('Leg_AnklePin',(.383,.016,.146),.019,.008)
 # Compact footprint with a heel, instep and three independently shaped toes.
 box('Foot_NewSole',(.315,-.038,.018),(.222,.315,.036),'Frame',.012)
 box('Foot_HeelShell',(.315,.065,.071),(.172,.108,.09),'Ivory',.016)
 box('Foot_InstepCore',(.315,-.023,.064),(.164,.151,.072),'Frame',.013)
 panel('Foot_AnkleCuff',[(.253,.1),(.268,.15),(.31,.163),(.351,.145),(.368,.095),(.348,.076),(.271,.078)],-.041,.077)
 for i,dx in enumerate([-.069,0,.069]):
  cx=.315+dx;w=.062;yf=-.19;yb=-.067
  verts=[p(cx+x,y,z) for x,y,z in [(-w/2,yf,.033),(w/2,yf,.033),(w/2,yb,.033),(-w/2,yb,.033),(-w/2,yf,.071),(w/2,yf,.071),(w/2,yb,.107),(-w/2,yb,.107)]]
  faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
  H['finish_mesh']('Foot_ToeShell_'+str(i)+'.'+side,verts,faces,C,M['Ivory'],bevel=.008)
  box('Foot_ToeBumper_'+str(i),(cx,-.19,.049),(.034,.013,.032),'Gold',.004)
  cyl('Foot_ToePivot_'+str(i),(cx,-.062,.063),.017,.054,axis=(1,0,0))
 for i in range(3):box('Foot_SoleTread_'+str(i),(.315,-.133+i*.087,.009),(.229,.018,.016),'Frame',.003)
bpy.context.view_layer.update()
sc=bpy.context.scene;cam=sc.camera
cam.location=(1.2,-2,1.0);cam.rotation_euler=(Vector((.27,-.015,.43))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.97
sc.render.resolution_x=900;sc.render.resolution_y=1200
sc.render.filepath=r'D:\codex+blender\model\legs_feet_reference_detail.png';bpy.ops.render.render(write_still=True)
cam.location=(2.6,-4.5,2.5);cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2
sc.render.resolution_x=900;sc.render.resolution_y=1000
sc.render.filepath=r'D:\codex+blender\model\legs_feet_reference_full.png';bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot_legs_feet_refined.blend')
print('Saved symmetric leg and compact foot refinement. Old armor retained hidden; original hip, knee and ankle centers preserved.')
