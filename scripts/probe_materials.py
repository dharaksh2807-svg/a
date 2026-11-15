import bpy,collections
for o in bpy.data.objects:
 if o.type=='MESH' and any(x in o.name for x in ['hair cap','ponytail','bomber shell','face identity']):
  print(o.name,collections.Counter(p.material_index for p in o.data.polygons),[m.name for m in o.data.materials])
  for m in o.data.materials:
   for n in m.node_tree.nodes:
    if n.type=='BSDF_PRINCIPLED':print(m.name,'color',tuple(n.inputs['Base Color'].default_value),'rough',n.inputs['Roughness'].default_value,'metal',n.inputs['Metallic'].default_value,'spec',n.inputs['Specular IOR Level'].default_value)
