import bpy,bmesh,json,math,struct,re
from pathlib import Path
OUT=Path(r'D:\codex+blender\model\web-viewer\public\models');OUT.mkdir(parents=True,exist_ok=True)
source_scene=bpy.context.window.scene
source_active=bpy.context.view_layer.objects.active
source_selection=list(bpy.context.selected_objects)
source_path=bpy.data.filepath
objects=[o for o in source_scene.objects if o.type in ('MESH','CURVE') and o.parent and not o.hide_render and not o.hide_get()]
source_deps=bpy.context.evaluated_depsgraph_get()
temp=bpy.data.scenes.new('WEB_EXPORT_TEMP')
copied=[];temporary_materials=[];mat_cache={};manifest=[];tri_total=0
def region(name,center):
 low=name.lower()
 if any(x in low for x in ['helmet','visor','head','eye','antenna','ear_','jaw','cheek','crown']):return 'Head'
 if any(x in low for x in ['shoulder','pauldron','forearm','upperarm','upper_arm','bicep','elbow','wrist','hand','thumb','finger','knuckle','dorsal','mcp']):
  return 'Left arm' if center.x>0 else 'Right arm'
 if any(x in low for x in ['thigh','shin','calf','foot','toe','ankle','knee']):return 'Left leg' if center.x>0 else 'Right leg'
 if any(x in low for x in ['pelvis','hip','belt']):return 'Pelvis'
 return 'Torso'
try:
 for index,src in enumerate(objects):
  ev=src.evaluated_get(source_deps)
  data=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=False,depsgraph=source_deps)
  data.transform(src.matrix_world)
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
  ob=bpy.data.objects.new(src.name,data);temp.collection.objects.link(ob);copied.append(ob)
  mats=list(data.materials);data.materials.clear()
  for original in mats:
   if not original:continue
   if original.name not in mat_cache:
    mat=bpy.data.materials.new('Web_'+original.name);mat.use_nodes=True
    node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    old=next((n for n in original.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if original.use_nodes else None
    node.inputs['Base Color'].default_value=old.inputs['Base Color'].default_value if old else original.diffuse_color
    node.inputs['Metallic'].default_value=old.inputs['Metallic'].default_value if old else .1
    node.inputs['Roughness'].default_value=.32 if 'Ivory' in original.name else (.28 if 'Gold' in original.name else .38)
    if old:
     for key in ['Emission Color','Emission Strength','Transmission Weight','IOR']:
      if key in old.inputs and key in node.inputs:node.inputs[key].default_value=old.inputs[key].default_value
    mat_cache[original.name]=mat;temporary_materials.append(mat)
   data.materials.append(mat_cache[original.name])
  if not data.materials:
   mat=next(iter(mat_cache.values()));data.materials.append(mat)
  if len(data.polygons)>6500:
   dec=ob.modifiers.new('Web geometry reduction','DECIMATE');dec.ratio=max(.12,6500/len(data.polygons));dec.use_collapse_triangulate=True
  center=sum((v.co for v in data.vertices),__import__('mathutils').Vector())/max(1,len(data.vertices))
  ob['sourceName']=src.name;ob['region']=region(src.name,center)
  label=re.sub(r'^(Attach|Finish|Ref16|Target|RefHead|Ref|Final|Preview|Leg|Arm|Torso|Pelvis|Head)[_ ]','',src.name,flags=re.I)
  label=re.sub(r'\.([LR])$',lambda m:' / '+('left' if m.group(1)=='L' else 'right'),label).replace('_',' ')
  ob['label']=label
  manifest.append({'sourceName':src.name,'region':ob['region'],'label':label,'sourcePolygons':len(data.polygons)})
 bpy.context.window.scene=temp
 for ob in temp.objects:ob.select_set(True)
 bpy.context.view_layer.objects.active=copied[0]
 bpy.context.view_layer.update()
 result=bpy.ops.export_scene.gltf(filepath=str(OUT/'robo-jack.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_animations=False,export_cameras=False,export_lights=False,export_yup=True,export_texcoords=False)
 raw=(OUT/'robo-jack.glb').read_bytes();length,kind=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+length].decode())
 mesh_nodes=[n for n in doc.get('nodes',[]) if 'mesh' in n]
 assert len(mesh_nodes)==len(objects),(len(mesh_nodes),len(objects))
 assert all(n.get('extras',{}).get('sourceName') for n in mesh_nodes)
 report={'sourceBlend':source_path,'objects':len(objects),'glbBytes':len(raw),'gltfVersion':doc['asset']['version'],'parts':manifest}
 (OUT/'manifest.json').write_text(json.dumps(report,indent=2))
 print('EXPORT VERIFIED:',len(mesh_nodes),'named selectable nodes;',round(len(raw)/1048576,2),'MB;',result)
finally:
 bpy.context.window.scene=source_scene
 for ob in list(copied):
  data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
  if data.users==0:bpy.data.meshes.remove(data)
 bpy.data.scenes.remove(temp)
 for mat in temporary_materials:
  if mat.users==0:bpy.data.materials.remove(mat)
 for ob in source_selection:
  if ob.name in bpy.data.objects:ob.select_set(True)
 if source_active and source_active.name in bpy.data.objects:bpy.context.view_layer.objects.active=source_active
 print('Restored original Blender scene; no source geometry changed.')
