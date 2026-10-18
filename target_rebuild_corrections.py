import bpy,math
from pathlib import Path
from mathutils import Vector
H={};exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=bpy.data.collections['PH15_Target_Shape_Rebuild'];M=H['mats']()
def box(n,p,s,m='Frame',b=.006):return H['box'](n,p,s,C,M[m],b)
for s,side in [(1,'L'),(-1,'R')]:
 old=bpy.data.objects['Thigh_Core.'+side];old.hide_render=True;old.hide_set(True)
 H['segment_box']('Target_ThighInnerFrame.'+side,(s*.14,.025,.806),(s*.2,-.018,.54),.079,.086,C,M['Frame'],bevel=.012)
 # Move thigh jacket forward enough to cover its core in front view.
 jacket=bpy.data.objects['Target_ThighJacket.'+side]
 for v in jacket.data.vertices:
  if v.co.y<.015:v.co.y-=.026
 # Restore compact grounded foot assemblies, with arched instep and jointed toes.
 cx=s*.28
 outline=[(-.073,-.188),(.073,-.188),(.097,-.15),(.098,-.067),(.084,.06),(.057,.09),(-.057,.09),(-.084,.06),(-.098,-.067),(-.097,-.15)]
 v=[(cx+s*x,y,z) for z in [.003,.033] for x,y in outline];n=len(outline)
 f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 H['finish_mesh']('Target_ContouredSole.'+side,v,f,C,M['Frame'],bevel=.009)
 H['loft']('Target_HeelHousing.'+side,[(.033,.164,.163,cx,.007),(.055,.17,.166,cx,.008),(.093,.146,.145,cx,.019),(.123,.112,.092,cx,.02)],C,M['Ivory'],bevel=.012)
 for i,dx in enumerate([-.06,0,.06]):
  x=cx+s*dx;w=.055
  v=[(x+xx,y,z) for xx,y,z in [(-w/2,-.181,.031),(w/2,-.181,.031),(w/2,-.067,.031),(-w/2,-.067,.031),(-w/2,-.181,.073),(w/2,-.181,.073),(w/2,-.067,.108),(-w/2,-.067,.108)]]
  H['finish_mesh']('Target_FittedToe_'+str(i)+'.'+side,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],C,M['Ivory'],bevel=.010)
  box('Target_ToeGold_'+str(i)+'.'+side,(x,-.183,.049),(.028,.008,.024),'Gold',.004)
 # Top metatarsal bridge follows the incline, rather than an exposed blank block.
 H['segment_box']('Target_InstepGuard.'+side,(cx,-.047,.105),(cx,.012,.14),.104,.033,C,M['Ivory'],bevel=.011)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot_target_rebuilt.blend')
print('Corrected thigh coverage and restored complete grounded mechanical feet.')
