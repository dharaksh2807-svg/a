import bpy,json
out={}
for name in ['NYRA · tailored track pants','NYRA · fitted sneaker uppers and laces']:
 o=bpy.data.objects[name];mesh=o.data;adj=[set() for v in mesh.vertices]
 for e in mesh.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
 seen=set();rows=[]
 for v in mesh.vertices:
  if v.index in seen:continue
  stack=[v.index];group=set(stack);seen.update(stack)
  while stack:
   for j in adj[stack.pop()]:
    if j not in seen:seen.add(j);group.add(j);stack.append(j)
  points=[mesh.vertices[i].co for i in group]
  if len(group)>10:rows.append({'n':len(group),'min':[round(min(p[i] for p in points),4) for i in range(3)],'max':[round(max(p[i] for p in points),4) for i in range(3)]})
 out[name]=rows
print(json.dumps(out,indent=2))
