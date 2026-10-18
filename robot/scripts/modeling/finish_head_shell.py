import bpy, math, json
from pathlib import Path
from mathutils import Vector
H={}
exec(compile(Path(r'D:\codex+blender\my-first-project\scripts\phase1_robot_blockout.py').read_text(),'helpers','exec'),H)
C=H['collection']('PH13_Head_ContinuousShell');M=H['mats']()
for o in list(C.objects):bpy.data.objects.remove(o,do_unlink=True)
old=bpy.data.objects['RefHead_RearHelmet'];old.hide_render=True;old.hide_set(True)
outer=[(-.16,1.604),(-.088,1.64),(.085,1.64),(.164,1.605),(.187,1.565),(.178,1.461),(.126,1.402),(-.125,1.402),(-.18,1.461),(-.187,1.566)]
# Match the exact rear contour of the visor frame, then sweep continuously to the rear.
sections=[(-.170,1,1,0),(-.115,1.035,1.035,.003),(-.035,1.04,1.08,.004),(.045,1.00,1.065,.003),(.115,.84,.88,0),(.163,.56,.61,0),(.187,.18,.24,0)]
verts=[];faces=[];n=len(outer)
for y,sx,sz,dz in sections:
 for x,z in outer:verts.append((x*sx,y,1.522+(z-1.522)*sz+dz))
for j in range(len(sections)-1):
 for i in range(n):
  a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
faces.append(tuple(range((len(sections)-1)*n,len(sections)*n)))
ob=H['finish_mesh']('Head_ContinuousHelmetShell',verts,faces,C,M['Ivory'],bevel=.011,smooth=True)
sol=H['modifier'](ob,'Helmet inner thickness','SOLIDIFY');sol.thickness=.007
# Seat both antenna roots into the roof rather than leaving them perched above it.
for sign,side in [(1,'L'),(-1,'R')]:
 H['box']('Head_AntennaSeat.'+side,(sign*.145,.025,1.628),(.057,.078,.052),C,M['Frame'],bevel=.009)
 # Rear panels and exhaust provide a finished rear view.
 H['box']('Head_RearVentHousing.'+side,(sign*.062,.173,1.522),(.062,.028,.077),C,M['Frame'],bevel=.009)
 for i in range(3):H['box']('Head_RearVent_'+str(i)+'.'+side,(sign*.062,.19,1.502+i*.019),(.044,.009,.006),C,M['Ivory'],bevel=.002)
bpy.data.objects['RefHead_CrownInset'].location.z-=.012
# Rear central status inset, seated in the shell.
H['box']('Head_RearStatus',(0,.192,1.529),(.032,.012,.013),C,M['Cyan'],bevel=.003)
bpy.context.view_layer.update()
sc=bpy.context.scene;cam=sc.camera
out=Path(r'D:\codex+blender\model\robot\renders\reviews\head_review');out.mkdir(exist_ok=True)
views={'front':(0,-3,1.56),'back':(0,3,1.56),'left':(3,0,1.56),'right':(-3,0,1.56),'front_threequarter':(1.6,-3,1.9),'back_threequarter':(-1.6,3,1.9),'top':(0,0,4),'underside':(0,-1,0)}
for name,eye in views.items():
 target=Vector((0,0,1.565));cam.location=eye;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.71
 sc.render.resolution_x=650;sc.render.resolution_y=650;sc.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
# Contact sheet generated from the actual rendered views.
import numpy as np
sheet=np.ones((650*2,650*4,4),dtype=np.float32)
for idx,name in enumerate(views):
 im=bpy.data.images.load(str(out/(name+'.png')),check_existing=False)
 arr=np.array(im.pixels[:],dtype=np.float32).reshape((650,650,4))
 row=1-idx//4;col=idx%4;sheet[row*650:(row+1)*650,col*650:(col+1)*650]=arr
 bpy.data.images.remove(im)
im=bpy.data.images.new('Head_AllSides_Review',width=2600,height=1300,alpha=True);im.pixels.foreach_set(sheet.ravel());im.filepath_raw=str(out/'all_sides.png');im.file_format='PNG';im.save()
print('Contact sheet order: front, back, left, right / front three-quarter, back three-quarter, top, underside')
cam.location=(2.6,-4.5,2.5);cam.rotation_euler=(Vector((0,0,.91))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.2
sc.render.resolution_x=900;sc.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath=r'D:\codex+blender\model\robot\blender\history\robot_head_shell_reviewed.blend')
print('Continuous shell joins visor frame at Y=-0.170; roof, sidewalls, rear and antenna bases now connected.')
