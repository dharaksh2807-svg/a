"""Candidate A reconstruction. Run with Blender in background from this repository."""
import argparse
import json
import math
import random
import sys
import tempfile
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
NYRA = HERE.parent
BASE = NYRA / "candidates/candidate-a/renders/original/nyra-review.blend"
parser = argparse.ArgumentParser()
parser.add_argument("--preview", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
preview_root = Path(tempfile.mkdtemp(prefix="nyra-reconstruction-")) if args.preview else None
TEXTURES = (preview_root or HERE) / "textures"
TEXTURES.mkdir(exist_ok=True)
if preview_root:
    print(f"Preview output: {preview_root}",flush=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE))
scene = bpy.context.scene
source = bpy.data.objects["Mesh_0"]
matrix = source.matrix_world.copy()
inverse = matrix.inverted()
tree = BVHTree.FromObject(source, bpy.context.evaluated_depsgraph_get())
rng = random.Random(731)

def collection(name):
    result = bpy.data.collections.new(name)
    scene.collection.children.link(result)
    return result

anatomy = collection("01 | Candidate A anatomy and fitted surfaces")
face = collection("02 | Face, eyes and jewelry")
hair = collection("03 | Scalp, bangs, ponytail and cards")
wardrobe = collection("04 | Technical outfit")
hardware = collection("05 | Utility accessories")
sneakers = collection("06 | Court runner sneakers")
archive = collection("90 | Original Candidate A, hidden")
for col in list(source.users_collection):
    col.objects.unlink(source)
archive.objects.link(source)
source.hide_set(True)
source.hide_render = True
source.name = "Candidate A | original atlas and surface"
bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection

def srgb(hex_color):
    channels = [int(hex_color[i:i+2], 16)/255 for i in (0,2,4)]
    return tuple(((c+.055)/1.055)**2.4 if c>.04045 else c/12.92 for c in channels)

def material(name, color, rough=.45, metal=0, *, bump=0, fuzz=0, coat=0, sss=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*srgb(color), 1)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bs = nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = mat.diffuse_color
    for key, value in {"Roughness":rough, "Metallic":metal, "Sheen Weight":fuzz, "Coat Weight":coat,
                       "Subsurface Weight":sss, "Subsurface Scale":.016}.items():
        bs.inputs[key].default_value = value
    if bump:
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 850 if sss else 510
        tex.inputs["Detail"].default_value = 2
        texcoord = nodes.new("ShaderNodeTexCoord")
        links.new(texcoord.outputs["Object"], tex.inputs["Vector"])
        fine = nodes.new("ShaderNodeBump")
        fine.inputs["Strength"].default_value = bump
        fine.inputs["Distance"].default_value = .00045
        links.new(tex.outputs["Fac"], fine.inputs["Height"])
        links.new(fine.outputs["Normal"], bs.inputs["Normal"])
    return mat

skin = material("Skin | warm peach, pores and scattering", "C28269", .45, sss=.11, bump=.24)
skin_face = skin.copy()
skin_face.name = "Face | painted skin variation and freckles"
nodes = skin_face.node_tree.nodes
attr = nodes.new("ShaderNodeVertexColor")
attr.layer_name = "Skin tint"
skin_face.node_tree.links.new(attr.outputs["Color"], nodes.get("Principled BSDF").inputs["Base Color"])
crease = material("Skin | muted warm crease", "915247", .6, sss=.09)
lip = material("Lip | warm rose vermilion", "A94C48", .44, coat=.11, sss=.12, bump=.12)
lip_upper = material("Lip | upper vermilion", "95443F", .48, sss=.12, bump=.13)
mouth = material("Mouth slit and nostril interiors", "402027", .58)
eye_white = material("Sclera | ivory, moist", "DFD3CC", .22, coat=.20, sss=.06)
liner = material("Lashes and brows", "261917", .56)
graphite = material("Legging | graphite elastane", "1F202B", .53, bump=.16, fuzz=.25)
top = material("Crop top | black double knit", "1A1821", .48, bump=.18, fuzz=.22)
violet = material("Technical violet | woven insert", "7739B0", .43, bump=.14, fuzz=.22)
deep = material("Purple ribbing, piping and binding", "362147", .56, fuzz=.20)
jacket = material("Jacket | aubergine coated nylon", "64328A", .46, bump=.14, fuzz=.18, coat=.05)
white = material("Jacket | cool pearl sleeve panels", "DCD4E9", .44, bump=.16, fuzz=.20)
glove = material("Glove and pouch | charcoal grain leather", "24212C", .49, bump=.24)
rubber = material("Outsole | violet rubber", "522B75", .55, bump=.18)
midsole = material("Midsole | off-white EVA", "E5DEEC", .48, bump=.13)
toe = material("Shoe | charcoal technical mesh", "25242D", .57, bump=.24, fuzz=.20)
pearl = material("Shoe | pale bonded overlays", "B6ABCA", .4, bump=.12)
laces = material("Shoe | violet braided laces", "895AC5", .52, fuzz=.22)
steel = material("Hardware | brushed silver", "B8AEBE", .28, .83)
gem = material("Pendant | violet enamel", "892DD2", .23, .25, coat=.44)
hair_colors = [material(f"Hair | {n}", c, r+.11, coat=.04) for n,c,r in [
    ("espresso", "241617", .34), ("black cherry", "311E24", .36), ("walnut", "3B2521", .35),
    ("muted rosewood", "3A2426", .36), ("violet dyed lock", "6D279F", .36), ("violet glint", "873EC1", .35)]]
for mat in hair_colors:
    bs = mat.node_tree.nodes.get("Principled BSDF")
    anisotropy = bs.inputs.get("Anisotropic")
    if anisotropy is not None:
        anisotropy.default_value = .35

def save_map(name, pixels, data=False):
    height,width,channels=pixels.shape
    assert channels==4
    image=bpy.data.images.new(name,width=width,height=height,alpha=True,is_data=data)
    image.pixels.foreach_set(np.asarray(pixels,dtype=np.float32).reshape(-1))
    image.file_format="PNG"
    image.filepath_raw=str(TEXTURES/f"{name}.png")
    image.save()
    image.pack()
    image.filepath="//textures/"+image.name+".png"
    return image

# The visible eye has a real curved corneoscleral surface and a baked pigment
# map. The recessed globe provides the independent eye body behind the lids.
iris_x,iris_z=np.meshgrid(np.linspace(-.022,.022,512),np.linspace(-.022,.022,512))
iris_r=np.sqrt(iris_x**2+iris_z**2)
iris_angle=np.arctan2(iris_z,iris_x)
iris_pixels=np.ones((512,512,4),dtype=np.float32)
sclera_tint=np.array(srgb("DFD4CC"))[None,None,:]
pink_tint=np.array(srgb("AF746A"))[None,None,:]
pink=np.clip((np.abs(iris_x)-.009)/.014,0,1)**1.35
iris_pixels[:,:,:3]=sclera_tint*(1-pink[:,:,None]) + pink_tint*pink[:,:,None]
grain=.50+.16*np.sin(31*iris_angle+680*iris_r)+.16*np.sin(67*iris_angle+900*iris_r)+.14*np.cos(109*iris_angle+1400*iris_r)
ring=np.clip((.0078-iris_r)/.00070,0,1)
inner=np.array(srgb("B17A46"))[None,None,:]
outer=np.array(srgb("3D231B"))[None,None,:]
pigment=np.clip(grain*ring,0,1)[:,:,None]
iris_rgb=inner*pigment+outer*(1-pigment)
iris_rgb[iris_r<.0031]=srgb("110D12")
mask=iris_r<=.00785
iris_pixels[:,:,:3][mask]=iris_rgb[mask]
eye_map=save_map("eye-brown-pigment",iris_pixels)
visible_eye=eye_white.copy()
visible_eye.name="Eye | corneoscleral cap with brown iris map"
wet=visible_eye.node_tree.nodes.get("Principled BSDF")
wet.inputs["Roughness"].default_value=.27
wet.inputs["Coat Weight"].default_value=.09
wet.inputs["Specular IOR Level"].default_value=.28
im=visible_eye.node_tree.nodes.new("ShaderNodeTexImage")
im.image=eye_map
visible_eye.node_tree.links.new(im.outputs["Color"],visible_eye.node_tree.nodes.get("Principled BSDF").inputs["Base Color"])

def mesh(name, verts, faces, col, mats, uv=None, indices=None):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    ob = bpy.data.objects.new(name, data)
    col.objects.link(ob)
    for mat in mats:
        data.materials.append(mat)
    for poly in data.polygons:
        poly.use_smooth = True
        if indices is not None:
            poly.material_index = indices[poly.index]
    if uv is not None:
        layer = data.uv_layers.new(name="Surface UV")
        for poly in data.polygons:
            us = [uv[i][0] for i in poly.vertices]
            seam = max(us)-min(us) > .75
            for li in poly.loop_indices:
                u,v = uv[data.loops[li].vertex_index]
                layer.data[li].uv = (u+1 if seam and u < .2 else u, v)
    return ob

def recalc(ob):
    import bmesh
    edit = bmesh.new()
    edit.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(edit, faces=list(edit.faces))
    edit.to_mesh(ob.data)
    edit.free()

def loft(name, rows, col, mats, *, caps=True, choose=None):
    n = len(rows[0])
    verts = [co for row in rows for co in row]
    faces = [(j*n+i, j*n+(i+1)%n, (j+1)*n+(i+1)%n, (j+1)*n+i)
             for j in range(len(rows)-1) for i in range(n)]
    slots = [choose(j,i,n) if choose else 0 for j in range(len(rows)-1) for i in range(n)]
    if caps:
        faces.extend([tuple(range(n-1,-1,-1)), tuple((len(rows)-1)*n+i for i in range(n))])
        slots.extend([0,0])
    uv = [(i/n,j/(len(rows)-1)) for j in range(len(rows)) for i in range(n)]
    obj = mesh(name, verts, faces, col, mats, uv, slots)
    recalc(obj)
    return obj

def sample(table, at):
    """Cubic Hermite blend through artist-controlled landmarks."""
    axis = [row[0] for row in table]
    i = max(0, min(len(axis)-2, int(np.searchsorted(axis,at))-1))
    w = axis[i+1]-axis[i]
    t = max(0,min(1,(at-axis[i])/w))
    p0,p1 = np.array(table[i][1:]),np.array(table[i+1][1:])
    a,b = max(0,i-1),min(len(axis)-1,i+2)
    d0 = (p1-np.array(table[a][1:])) * w/(axis[i+1]-axis[a])
    d1 = (np.array(table[b][1:])-p0) * w/(axis[b]-axis[i])
    return (2*t**3-3*t*t+1)*p0+(t**3-2*t*t+t)*d0+(-2*t**3+3*t*t)*p1+(t**3-t*t)*d1

def gauss(x,z,cx,cz,wx,wz):
    return math.exp(-((x-cx)/wx)**2-((z-cz)/wz)**2)

def tube(name, points, width, depth, col, mats, *, steps=34, segments=12, slots=None, axis=(1,0,0)):
    # Points are (x,y,z,width multiplier,depth multiplier).
    curve = [(i,*p) for i,p in enumerate(points)]
    rows=[]
    direction=Vector(axis)
    for i in range(steps+1):
        t=(len(points)-1)*i/steps
        x,y,z,sx,sy=sample(curve,t)
        p=Vector((x,y,z))
        tangent=Vector(sample(curve,min(t+.025,len(points)-1))[:3]-sample(curve,max(t-.025,0))[:3]).normalized()
        u=direction-tangent*direction.dot(tangent)
        if u.length < .05:
            u=Vector((0,1,0))-tangent*tangent.y
        u.normalize()
        v=tangent.cross(u)
        rows.append([p+u*math.cos(a)*width*max(.016,sx)+v*math.sin(a)*depth*max(.016,sy)
                     for a in np.linspace(0,2*math.pi,segments,endpoint=False)])
    return loft(name, rows, col, mats, choose=slots)

def line(name, points, radii, col, mat, diameter=.001, closed=False):
    cu=bpy.data.curves.new(name,"CURVE")
    cu.dimensions="3D"
    cu.resolution_u=12
    cu.bevel_depth=diameter
    cu.bevel_resolution=2
    cu.use_fill_caps=True
    path=cu.splines.new("BEZIER")
    path.bezier_points.add(len(points)-1)
    for bp,p,r in zip(path.bezier_points,points,radii):
        bp.co=p
        bp.radius=r
        bp.handle_left_type=bp.handle_right_type="AUTO"
    path.use_cyclic_u=closed
    ob=bpy.data.objects.new(name,cu)
    col.objects.link(ob)
    cu.materials.append(mat)
    return ob

def ellipsoid(name, center, dims, col, mat, segments=40, rings=24, rot=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=center)
    ob=bpy.context.object
    ob.name=name
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)
    for v in ob.data.vertices:
        v.co.x*=dims[0]
        v.co.y*=dims[1]
        v.co.z*=dims[2]
    if rot:
        ob.rotation_euler=rot
    ob.data.materials.append(mat)
    for poly in ob.data.polygons:
        poly.use_smooth=True
    return ob

def box(name, center, dims, bevel, col, mat, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    ob=bpy.context.object
    ob.name=name
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)
    for v in ob.data.vertices:
        for i in range(3):
            v.co[i]*=dims[i]
    if rot:
        ob.rotation_euler=rot
    edge=ob.modifiers.new("Rounded construction edge","BEVEL")
    edge.width=bevel
    edge.segments=3
    normal=ob.modifiers.new("Weighted panel normals","WEIGHTED_NORMAL")
    ob.data.materials.append(mat)
    return ob

# Head planes are drawn in Candidate A's world space. Y is depth; negative is front.
head_spec = [
    (1.505,.006,.005,-.015), (1.517,.029,-.015,-.060),
    (1.530,.047,-.005,-.084), (1.546,.060,.008,-.092),
    (1.568,.069,.015,-.093), (1.596,.076,.022,-.095),
    (1.627,.077,.024,-.095), (1.662,.075,.025,-.101),
    (1.693,.066,.027,-.091), (1.721,.045,.028,-.063),
    (1.739,.021,.029,-.025), (1.744,.003,.028,.020),
]

def face_point(theta,z):
    width,center,front=sample(head_spec,z)
    x=width*math.sin(theta)
    c=math.cos(theta)
    if c < 0:
        return (x,center-.092*c*min(1,width/.058),z)
    y=center-(center-front)*c**.74
    # Nasal bridge, cartilage and alae; cheek and brow volumes; medial eye socket.
    end=gauss(x,z,0,1.582,.014,.012)
    detail=-.016*gauss(x,z,0,1.620,.009,.031)-.023*end
    detail-=.010*(gauss(x,z,.012,1.577,.007,.007)+gauss(x,z,-.012,1.577,.007,.007))
    detail-=.004*gauss(x,z,0,1.561,.028,.016)
    detail+=.0027*(gauss(x,z,.0095,1.575,.0048,.0036)+gauss(x,z,-.0095,1.575,.0048,.0036))
    detail-=.006*gauss(x,z,0,1.531,.028,.011)
    detail-=.010*(gauss(x,z,.047,1.595,.027,.020)+gauss(x,z,-.047,1.595,.027,.020))
    detail-=.006*(gauss(x,z,.030,1.648,.030,.010)+gauss(x,z,-.030,1.648,.030,.010))
    detail+=.004*(gauss(x,z,.032,1.626,.025,.009)+gauss(x,z,-.032,1.626,.025,.009))
    return (x,y+detail,z)

def facial_y(x,z):
    return face_point(math.asin(max(-1,min(1,x/sample(head_spec,z)[0]))),z)[1]

def eye_pos(side,phi):
    h=math.cos(phi)
    v=math.sin(phi)
    x=.032+.0165*h
    z=1.626+.0017*h+(.0071 if v>0 else .0052)*v*(.80+.20*abs(v))
    y=facial_y(x,z)-.00065
    return (side*x,y,z)

theta=np.linspace(-math.pi,math.pi,192,endpoint=False)
heights=np.linspace(1.505,1.744,132)
nz,nt=len(heights),len(theta)
verts=[face_point(t,z) for z in heights for t in theta]
uv=[(i/nt,j/(nz-1)) for j in range(nz) for i in range(nt)]
boxes=[]
for sign in [-1,1]:
    cols=np.flatnonzero((theta>sign*.435-.33)&(theta<sign*.435+.33))
    rows=np.flatnonzero((heights>1.608)&(heights<1.6445))
    boxes.append((cols[0],cols[-1],rows[0],rows[-1],sign))
faces=[]
for j in range(nz-1):
    for i in range(nt):
        if any(a<=i<b and c<=j<d for a,b,c,d,_ in boxes):
            continue
        ii=(i+1)%nt
        faces.append((j*nt+i,j*nt+ii,(j+1)*nt+ii,(j+1)*nt+i))
faces.extend([tuple(range(nt-1,-1,-1)),tuple((nz-1)*nt+i for i in range(nt))])
for left,right,bottom,upper,sign in boxes:
    perim=[(i,bottom) for i in range(left,right)]+[(right,j) for j in range(bottom,upper)]+[(i,upper) for i in range(right,left,-1)]+[(left,j) for j in range(upper,bottom,-1)]
    previous=[j*nt+i for i,j in perim]
    count=len(perim)
    for k in range(1,9):
        row=[]
        t=k/8
        for i,j in perim:
            p=np.array(verts[j*nt+i])
            phi=math.atan2((j-(bottom+upper)/2)/((upper-bottom)/2),sign*(i-(left+right)/2)/((right-left)/2))
            aperture=np.array(eye_pos(sign,phi))
            co=p*(1-t)+aperture*t
            # Keep the outer tangents identical to the sculpted face. Offset
            # only the last rings into the eyelid edge to feather the orbit.
            correction=aperture[1]-facial_y(aperture[0],aperture[2])
            blend=t*t*(3-2*t)
            co[1]=facial_y(co[0],co[2])+correction*blend
            co[1]-=.00045*math.sin(math.pi*t)**2*abs(math.sin(phi))
            row.append(len(verts))
            verts.append(tuple(co))
            local_theta=math.asin(max(-1,min(1,co[0]/sample(head_spec,co[2])[0])))
            uv.append(((local_theta+math.pi)/(2*math.pi),(co[2]-heights[0])/(heights[-1]-heights[0])))
        faces.extend([(previous[i],previous[(i+1)%count],row[(i+1)%count],row[i]) for i in range(count)])
        previous=row
head=mesh("Face | rebuilt orbital loops and sculpted planes",verts,faces,face,[skin_face],uv)
# Remove unused grid vertices from the eye openings; all bridge loops stay editable.
import bmesh
bm=bmesh.new()
bm.from_mesh(head.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_edges],context="VERTS")
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(head.data)
bm.free()
color=head.data.color_attributes.new(name="Skin tint",type="FLOAT_COLOR",domain="POINT")
freckle_sites=[(rng.uniform(-.061,.061),rng.uniform(1.579,1.618),rng.uniform(.00055,.0016)) for _ in range(310)]
cold=np.array(srgb("C98F77"))
warm=np.array(srgb("B96557"))
tint=np.array(srgb("894C3D"))
for vert in head.data.vertices:
    x,y,z=vert.co
    blush=.39*(gauss(x,z,.048,1.589,.019,.016)+gauss(x,z,-.048,1.589,.019,.016))
    blush+=.17*gauss(x,z,0,1.583,.015,.012)
    blush+=.28*(gauss(x,z,.031,1.635,.025,.010)+gauss(x,z,-.031,1.635,.025,.010))
    f=max((gauss(x,z,fx,fz,w,w*.8) for fx,fz,w in freckle_sites if abs(x-fx)<.004 and abs(z-fz)<.004),default=0)
    base=cold*(1-blush)+warm*blush
    if y < -.045:
        base=base*(1-f*.29)+tint*f*.29
    color.data[vert.index].color=(*base,1)

for side in [-1,1]:
    L="L" if side>0 else "R"
    ellipsoid(f"{L} eye globe | recessed body", (side*.032,-.054,1.626),(.0165,.012,.0170),face,eye_white,48,24)
    lid_ring=[eye_pos(side,2*math.pi*i/96) for i in range(96)]
    points=[(side*.032,facial_y(.032,1.626)-.0061,1.626)]
    for j in range(1,21):
        r=j/20
        for x,_,z in lid_ring:
            xx=side*.032+(x-side*.032)*r
            zz=1.626+(z-1.626)*r
            points.append((xx,facial_y(xx,zz)-.00065-.00545*(1-r*r),zz))
    cap_faces=[(0,1+i,1+(i+1)%96) for i in range(96)]
    for j in range(19):
        for i in range(96):
            k=(i+1)%96
            cap_faces.append((1+j*96+i,1+(j+1)*96+i,1+(j+1)*96+k,1+j*96+k))
    if side<0:
        cap_faces=[tuple(reversed(f)) for f in cap_faces]
    # Eye is a deliberately open cap. Keep its winding toward the lens.
    if Vector(points[cap_faces[0][1]]-np.array(points[0])).cross(Vector(points[cap_faces[0][2]]-np.array(points[0]))).y>0:
        cap_faces=[tuple(reversed(f)) for f in cap_faces]
    uv_eye=[(.5+(x-side*.032)/.044,.5+(z-1.626)/.044) for x,_,z in points]
    mesh(f"{L} eye | convex sclera and mapped iris",points,cap_faces,face,[visible_eye],uv_eye)
    upper=[eye_pos(side,math.pi*i/18) for i in range(19)]
    low=[eye_pos(side,math.pi+math.pi*i/15) for i in range(16)]
    line(f"{L} upper lash line", [(x,y-.00042,z+.00015) for x,y,z in upper],
         [max(.44,math.sin(math.pi*i/18))*(1-.24*i/18) for i in range(19)],face,liner,.00107)
    line(f"{L} lower waterline",[(x,y-.00020,z-.00022) for x,y,z in low],
         [max(.16,math.sin(math.pi*i/15)) for i in range(16)],face,crease,.00046)
    for j in range(23):
        t=.075+.85*j/22
        x,y,z=eye_pos(side,math.pi*t)
        l=(.0017+.0021*math.sin(math.pi*t)**.57)*(.80+.30*rng.random())
        line(f"{L} eyelash {j:02d}",[(x,y-.0006,z),(x+side*l*.16,y-.0016,z+l*.62),(x+side*l*.59,y-.00165,z+l)],
             [.8,.67,.02],face,liner,.00023)
    # Brow with a taper and individual hair directions.
    brow_spec=[(0,.012,1.647,.0026),(.24,.023,1.651,.0043),(.56,.039,1.655,.0041),(.78,.052,1.653,.0029),(1,.064,1.647,.0002)]
    bv=[]; bf=[]
    for t in np.linspace(0,1,45):
        x,z,w=sample(brow_spec,t)
        for s in [-1,1]:
            zz=z+s*w/2
            bv.append((side*x,facial_y(x,zz)-.00060,zz))
    bf=[(i,i+1,i+3,i+2) for i in range(0,len(bv)-2,2)]
    mesh(f"{L} shaped brow",bv,bf,face,[liner])
    for j in range(40):
        t=.02+.95*j/39
        x,z,w=sample(brow_spec,t)
        zz=z-w*.48
        x2=x+(.0014+.0015*t)
        z2=z+w*.54
        line(f"{L} brow strand {j:02d}", [(side*x,facial_y(x,zz)-.0008,zz),
             (side*x2,facial_y(x2,z2)-.001,z2)], [.7,.07],face,liner,.00022)
    x=side*.0093
    z=1.5751
    ellipsoid(f"{L} nostril occlusion",(x,facial_y(x,z)+.00025,z),(.0030,.00063,.00118),face,mouth,28,14,rot=(.42,side*.19,side*.12))
    ellipsoid(f"{L} ear", (side*.074,.001,1.604), (.0125,.015,.024), face,skin,rot=(.1,side*.14,0))
    ellipsoid(f"{L} concha",(side*.080,-.009,1.605),(.007,.006,.014),face,crease)
    ear=[(side*(.078+.007*math.cos(t)),-.010+.006*math.cos(t),1.605+.020*math.sin(t)) for t in np.linspace(-math.pi*.48,math.pi*1.43,16)]
    line(f"{L} ear helix",ear,[.5]+[1]*14+[.44],face,skin,.003)
    earring=[(side*(.082+.005*math.cos(t)),-.008+.010*math.cos(t),1.573+.016*math.sin(t)) for t in np.linspace(0,2*math.pi,22,endpoint=False)]
    line(f"{L} silver hoop",earring,[1]*len(earring),face,steel,.00145,closed=True)

# Lips have a separate wet line and a sharp, asymmetric cupid's bow.
def lip_shape(t,top_curve):
    x=.0245*t
    taper=max(0,1-t*t)**.65
    seam=1.5554+.0017*t*t-.0006*math.cos(t*math.pi*2)
    swell=(.0049+.0022*math.exp(-((abs(t)-.30)/.19)**2)) if top_curve else .0070
    return x,seam,taper*swell*(1 if top_curve else -1),taper

for top_curve in [True,False]:
    lv=[]
    lf=[]
    for j in range(13):
        w=j/12
        for i in range(57):
            t=-1+2*i/56
            x,seam,height,amp=lip_shape(t,top_curve)
            z=seam+w*height+(.00027 if top_curve else -.00027)
            y=facial_y(x,z)-amp*(.0019*(1-w)+(.0036 if top_curve else .0036)*math.sin(math.pi*w)**.76)-.00032
            lv.append((x,y,z))
    lf=[(j*57+i,j*57+i+1,(j+1)*57+i+1,(j+1)*57+i) for j in range(12) for i in range(56)]
    shade=lip_upper if top_curve else lip
    painted=shade.node_tree.nodes.new("ShaderNodeVertexColor")
    painted.layer_name="Vermilion tint"
    shade.node_tree.links.new(painted.outputs["Color"],shade.node_tree.nodes.get("Principled BSDF").inputs["Base Color"])
    layer=mesh("Cupid's bow" if top_curve else "Lower vermilion",lv,lf,face,[shade],
         [(i/56,j/12) for j in range(13) for i in range(57)])
    tones=layer.data.color_attributes.new(name="Vermilion tint",type="FLOAT_COLOR",domain="POINT")
    for vert in layer.data.vertices:
        w=(vert.index//57)/12
        v=abs(vert.index%57-28)/28
        blend=1-max(0,(w-.62)/.38)**2
        blend*=1-max(0,(v-.86)/.14)**2
        rgb=cold*(1-blend)+np.array(shade.diffuse_color[:3])*blend
        tones.data[vert.index].color=(*rgb,1)
    bm=bmesh.new()
    bm.from_mesh(layer.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0000005)
    bm.to_mesh(layer.data)
    bm.free()
slit=[]
for t in np.linspace(-1,1,25):
    x,z,_,amp=lip_shape(t,True)
    slit.append((x,facial_y(x,z)-.0014*amp-.00017,z))
line("Defined oral fissure",slit,[max(.06,1-t*t) for t in np.linspace(-1,1,25)],face,mouth,.00042)

# Reconstruct the exposed torso independently of the dropped jacket. The body rings
# follow Candidate A's shoulder, waist and neck landmarks with a smoothed abdominal wall.
torso_spec=[
    (.978,.142,-.009,.088,.074), (1.013,.127,-.008,.076,.067),
    (1.054,.112,-.007,.068,.065), (1.094,.109,-.005,.072,.068),
    (1.140,.123,.002,.083,.075), (1.191,.137,.002,.097,.080),
    (1.230,.149,.004,.098,.083), (1.269,.158,.007,.083,.080),
    (1.308,.154,.005,.073,.076), (1.340,.132,.003,.065,.068),
    (1.370,.087,.001,.056,.065), (1.402,.054,-.003,.044,.056),
    (1.443,.044,-.000,.044,.050), (1.493,.045,.007,.043,.048),
    (1.521,.038,.011,.039,.044), (1.545,.033,.013,.033,.041),
]
def torso_point(z,t,offset=0):
    rx,cy,front,back=sample(torso_spec,z)
    c,s=math.cos(t),math.sin(t)
    x=(rx+offset)*s
    y=cy-((front if c>=0 else back)+offset)*c
    if c>0:
        y-=.024*(gauss(x,z,.066,1.229,.048,.038)+gauss(x,z,-.066,1.229,.048,.038))*c
        y-=.003*(gauss(x,z,.036,1.087,.024,.063)+gauss(x,z,-.036,1.087,.024,.063))
        y+=.0040*gauss(x,z,0,1.058,.0079,.0055)
        y+=.0016*gauss(x,z,0,1.10,.007,.063)
    return (x,y,z)

torso=loft("Torso and neck | independent skin",[[torso_point(z,t) for t in np.linspace(-math.pi,math.pi,112,endpoint=False)]
      for z in np.linspace(.978,1.545,166)],anatomy,[skin])
ellipsoid("Umbilical shadow",(0,torso_point(1.058,0)[1]+.0001,1.058),(.0029,.00125,.0011),anatomy,crease,24,12)

def crop_edge(t):
    f=max(0,math.cos(t))
    return 1.304+.078*math.exp(-((abs(t)-.62)/.245)**2)-.055*math.exp(-(t/.31)**2) if f>0 else 1.302+.05*math.exp(-((abs(t)-2.47)/.35)**2)
def top_point(t,f,off=.004):
    return torso_point(1.155+(crop_edge(t)-1.155)*f,t,off)
N=144
angles=np.linspace(-math.pi,math.pi,N,endpoint=False)
bra=loft("Black athletic crop top | independent shell",[[top_point(t,f) for t in angles] for f in np.linspace(0,1,43)],
         wardrobe,[top,violet,deep],caps=False,
         choose=lambda j,i,n:2 if j<4 else 0)
sol=bra.modifiers.new("Knit shell thickness","SOLIDIFY")
sol.thickness=.0016
for f in [0,.1,1]:
    line("Crop top bound seam",[top_point(t,f,.0056) for t in angles[::3]],[1]*48,wardrobe,deep,.0016,closed=True)
for side in [-1,1]:
    strip=[]
    for j in range(72):
        u=j/71
        f=.09+.87*u
        center=.65+.105*math.sin(math.pi*u)
        for i in range(9):
            a=side*(center+(i/4-1)*(.059-.015*u))
            strip.append(top_point(a,f,.0055))
    faces_strip=[(j*9+i,j*9+i+1,(j+1)*9+i+1,(j+1)*9+i) for j in range(71) for i in range(8)]
    mesh("Crop top violet panel",strip,faces_strip,wardrobe,[violet],[(i/8,j/71) for j in range(72) for i in range(9)])

# Bridge the front and rear shoulder peaks with a continuous knit strap.
for side in [-1,1]:
    vv=[]
    for u in np.linspace(0,1,43):
        for w in np.linspace(-1,1,11):
            a=side*(.62+.115*w)
            aa=side*(2.47-.115*w)
            start=np.array(top_point(a,.95,.0046))
            end=np.array(top_point(aa,.94,.0046))
            p=(1-u)*start+u*end
            p[2]+=.017*math.sin(math.pi*u)
            p[0]+=side*.035*math.sin(math.pi*u)
            vv.append(tuple(p))
    ff=[(j*11+i,j*11+i+1,(j+1)*11+i+1,(j+1)*11+i) for j in range(42) for i in range(10)]
    ob=mesh("Over-shoulder knit strap",vv,ff,wardrobe,[top],[(i/10,j/42) for j in range(43) for i in range(11)])
    mod=ob.modifiers.new("Strap thickness","SOLIDIFY")
    mod.thickness=.002

# Candidate A leg landmarks and measured surface. Angular radial samples are limited
# against an anatomical envelope to suppress raw faceting and projected pouches.
leg_spec=[(.168,.133,-.006,.028,.033),(.20,.132,-.001,.030,.037),(.25,.129,.009,.033,.041),
          (.34,.128,.020,.038,.048),(.43,.122,.025,.041,.050),(.52,.116,.022,.040,.048),
          (.575,.105,.010,.037,.046),(.64,.098,-.004,.042,.052),(.72,.092,-.015,.048,.063),
          (.78,.091,-.021,.056,.072),(.839,.089,-.019,.066,.077)]
grid_z=np.linspace(.168,.839,90)
grid_a=np.linspace(0,2*math.pi,64,endpoint=False)
measure=np.ones((len(grid_z),len(grid_a)))
for j,z in enumerate(grid_z):
    cx,cy,rx,ry=sample(leg_spec,z)
    for i,t in enumerate(grid_a):
        vector=Vector((rx*math.cos(t),-ry*math.sin(t),0))
        center=Vector((cx,cy,z))
        h=tree.ray_cast(inverse@center,inverse.to_3x3()@vector.normalized(),.09/matrix.to_scale().x)[0]
        if h is not None:
            fraction=(matrix@h-center).length/vector.length
            measure[j,i]=1+.47*(np.clip(fraction,.78,1.23)-1)
for _ in range(7):
    measure=(4*measure+np.roll(measure,1,1)+np.roll(measure,-1,1)
             +np.vstack([measure[0],measure[:-1]])+np.vstack([measure[1:],measure[-1]]))/8

def leg_point(z,t,s,off=0):
    cx,cy,rx,ry=sample(leg_spec,z)
    pos=(t%(2*math.pi))/(2*math.pi)*len(grid_a)
    k=int(pos)
    row=(z-grid_z[0])/(grid_z[-1]-grid_z[0])*(len(grid_z)-1)
    j=min(len(grid_z)-2,max(0,int(row)))
    f=(1-row+j)*((1-pos+k)*measure[j,k]+(pos-k)*measure[j,(k+1)%len(grid_a)])
    f+=(row-j)*((1-pos+k)*measure[j+1,k]+(pos-k)*measure[j+1,(k+1)%len(grid_a)])
    x=cx+(rx*f+off)*math.cos(t)
    y=cy-(ry*f+off)*math.sin(t)
    return s*x,y,z

pn=80
pt=np.linspace(0,2*math.pi,pn,endpoint=False)
pant_verts=[]; pant_uv=[]; pant_faces=[]
toprings=[]
for s in [1,-1]:
    offset=len(pant_verts)
    for j,z in enumerate(np.linspace(.180,.839,100)):
        for i,t in enumerate(pt):
            x,y,z=leg_point(z,t,s)
            pant_verts.append((x,y,z));pant_uv.append((i/pn,j/144))
    for j in range(99):
        for i in range(pn):
            ii=(i+1)%pn
            pant_faces.append(tuple(offset+k for k in [j*pn+i,j*pn+ii,(j+1)*pn+ii,(j+1)*pn+i]))
    top_row=[]
    for i,t in enumerate(pt):
        top_row.append(len(pant_verts))
        x=s*.156*max(0,math.cos(t))
        y=-.016-.086*math.sin(t)
        pant_verts.append((x,y,.900-.027*max(0,-math.cos(t))));pant_uv.append((i/pn,.74))
    for i in range(pn):
        ii=(i+1)%pn
        pant_faces.append((offset+99*pn+i,offset+99*pn+ii,top_row[ii],top_row[i]))
    toprings.append(top_row)
# An identical medial edge in the two rings welds into a single crotch path.
exterior=toprings[0][60:]+toprings[0][:21]+toprings[1][19::-1]+toprings[1][:60:-1]
previous=exterior
for j,z in enumerate(np.linspace(.903,1.021,35)):
    c=(z-.903)/.118
    current=[]
    for idx in exterior:
        x,y,_=pant_verts[idx]
        # The final waistband follows the retained torso exactly.
        t=math.atan2(x/.156,(-y-.016)/.086)
        tx,ty,_=torso_point(1.021,t,.005)
        current.append(len(pant_verts))
        pant_verts.append((x*(1-c)+tx*c,y*(1-c)+ty*c,z))
        pant_uv.append(((t+math.pi)/(2*math.pi),.75+c*.25))
    for i in range(len(current)):
        ii=(i+1)%len(current)
        pant_faces.append((previous[i],previous[ii],current[ii],current[i]))
    previous=current
pants=mesh("Candidate A fitted leggings | stitched leg and pelvis loops",pant_verts,pant_faces,wardrobe,[graphite],pant_uv)
bm=bmesh.new();bm.from_mesh(pants.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0000007)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(pants.data);bm.free()

transition=pants.vertex_groups.new(name="Pelvis and crotch blend")
for vert in pants.data.vertices:
    z=vert.co.z
    weight=min(1,max(0,(z-.805)/.045),max(0,(.964-z)/.035))
    if weight:
        transition.add([vert.index],weight,"REPLACE")
        if vert.co.y>0:
            vert.co.y+=.023*math.exp(-((z-.883)/.056)**2)*math.sin(min(1,abs(vert.co.x)/.136)*math.pi*.88)
smooth=pants.modifiers.new("Smooth crotch transition","SMOOTH")
smooth.factor=.62
smooth.iterations=17
smooth.vertex_group=transition.name

for s in [-1,1]:
    for side,flip in [("front",1),("rear",-1)]:
        vv=[]; ff=[]
        for j in range(66):
            u=j/65
            z=.49+.345*u
            t=flip*(1.63-1.17*u+.23*math.sin(math.pi*u))
            width=(.045+.36*math.sin(math.pi*u*.91)**.51)
            for i in range(11):
                a=t+(2*i/10-1)*width
                vv.append(leg_point(z,a,s,.00175))
        ff=[(j*11+i,j*11+i+1,(j+1)*11+i+1,(j+1)*11+i) for j in range(65) for i in range(10)]
        mesh(f"Violet {side} inset panel {s}",vv,ff,wardrobe,[violet],[(i/10,j/65) for j in range(66) for i in range(11)])
    for t in [-.055,.055]:
        line("Reflective side welt",[leg_point(z,t,s,.0020) for z in np.linspace(.206,.83,24)],[1]*24,wardrobe,pearl,.00085)
    loft("Turned ankle hem",[[leg_point(z,t,s,.0025) for t in pt] for z in [.180,.184,.192,.196]],
         wardrobe,[deep],caps=False)
    loft("Exposed ankle | fitted from source lower leg",[[leg_point(z,t,s,-.0025) for t in pt]
         for z in np.linspace(.168,.185,8)],anatomy,[skin])

# Sleeve and forearm profiles share Candidate A's pose. Folds are modeled at the
# shell surface and accent panels follow the same parameterization.
arm_spec=[
    (.956,.323,.052,.020,.022), (.992,.310,.048,.020,.020),
    (1.048,.287,.043,.024,.025), (1.106,.261,.038,.031,.031),
    (1.159,.237,.031,.034,.034), (1.213,.207,.026,.039,.038),
    (1.270,.179,.021,.047,.043), (1.312,.153,.019,.045,.043),
    (1.343,.143,.015,.039,.038), (1.361,.128,.014,.025,.026)]
sleeve_spec=[
    (1.088,.261,.034,.040,.039), (1.115,.250,.028,.046,.047),
    (1.145,.245,.025,.052,.053), (1.180,.228,.022,.056,.057),
    (1.220,.216,.019,.059,.060), (1.248,.202,.014,.055,.054),
    (1.278,.190,.010,.050,.047),
]
def arm_point(z,t,s,off=0):
    cx,cy,xr,yr=sample(arm_spec,z)
    return (s*(cx+(xr+off)*math.cos(t)),cy-(yr+off)*math.sin(t),z)
def sleeve_point(z,t,s,off=0):
    cx,cy,xr,yr=sample(sleeve_spec,z)
    u=(z-1.088)/.19
    fold=(.005*math.sin(6*math.pi*u+1.6*math.cos(2*t))+.0027*math.sin(9*math.pi*u-2.6*t))*math.sin(math.pi*u)**.7
    z+=.012*u**4*math.cos(t)
    return (s*(cx+(xr+fold+off)*math.cos(t)),cy-(yr+fold+off)*math.sin(t),z)
st=np.linspace(0,2*math.pi,96,endpoint=False)
for s in [-1,1]:
    # Skin limbs are separate to keep the area under the cuffs editable.
    loft(f"Arm {s} | Candidate A pose",[[arm_point(z,t,s) for t in st]
         for z in np.linspace(.956,1.361,80)],anatomy,[skin])
    ob=loft(f"Jacket sleeve {s} | draped nylon",[[sleeve_point(z,t,s) for t in st]
       for z in np.linspace(1.088,1.278,74)],wardrobe,[jacket,white,violet],caps=False,
       choose=lambda j,i,n: 1 if min(i,n-i)<n*.111 else 2 if min(i,n-i)<n*.145 else 0)
    mod=ob.modifiers.new("Woven sleeve thickness","SOLIDIFY");mod.thickness=.0028
    for t in [-.91,-.70,.70,.91]:
        line("Sleeve panel topstitch",[sleeve_point(z,t,s,.00145) for z in np.linspace(1.105,1.270,25)],
             [1]*25,wardrobe,deep,.00055)
    line("Dropped collar roll",[sleeve_point(1.278,t,s,.0023) for t in st[::3]],[1]*32,wardrobe,deep,.0046,closed=True)
    for trim in [-.50,math.pi+.50]:
        line("Zipper tape",[sleeve_point(z,trim,s,.0024) for z in np.linspace(1.133,1.276,18)],
             [1]*18,wardrobe,deep,.0019)
        for z in np.linspace(1.154,1.270,30):
            x,y,zz=sleeve_point(z,trim,s,.0031)
            box("Short zipper tooth",(x,y,zz),(.0030,.0020,.0013),.0004,hardware,steel)
    tip=sleeve_point(1.145,-.50,s,.003)
    box("Collar zipper pull",(tip[0],tip[1]-.001,tip[2]-.006),(.006,.003,.013),.001,hardware,steel)
    ob=loft(f"Rib-knit sleeve cuff {s}",[[
        (s*(sample(arm_spec,z)[0]+(.037+.0012*math.cos(i*2*math.pi/3))*math.cos(t)),
         sample(arm_spec,z)[1]-(.036+.0012*math.cos(i*2*math.pi/3))*math.sin(t),z)
        for i,t in enumerate(st)] for z in np.linspace(1.074,1.112,9)],wardrobe,[deep],caps=False)
    mod=ob.modifiers.new("Knit cuff thickness","SOLIDIFY");mod.thickness=.002

    # Hanging near-A pose, with separately modeled digits and fingerless cuffs.
    wrist=(s*.323,.052,.967)
    palm_tip=(s*.338,.053,.906)
    tube(f"Fingerless glove palm {s}",[(*wrist,1,.83),(s*.329,.053,.947,1.04,1),
         (*palm_tip,.90,.76)],.022,.016,wardrobe,[glove],axis=(1,0,0))
    for d in range(4):
        x=s*(.322+d*.010)
        offset=[-.002,.006,.006,.002][d]
        start=(x,.051+offset,.915+d*.0025)
        endz=.864+d*.0063
        tube(f"Finger {d+1} {s}",[(*start,1,1),(x+s*.003,.046+offset, .893+d*.0038,.86,.92),
             (x+s*.002,.039+offset,endz+.006,.65,.71),(x-s*.001,.036+offset,endz,.23,.35)],
             .0050 if d<3 else .0041,.0050,anatomy,[skin],steps=15,segments=10)
        tube("Fingerless knuckle cuff",[(*start,1,1),(x+s*.001,.050+offset,.905+d*.0026,.93,.90)],
             .0057,.0062,wardrobe,[glove],steps=5,segments=10)
    tube(f"Thumb {s}",[(s*.315,.046,.938,1,1),(s*.306,.035,.922,.86,.85),(s*.309,.031,.908,.72,.73),
         (s*.312,.029,.903,.22,.36)],.0069,.0067,anatomy,[skin],steps=18,segments=12)
    tube("Glove thumb cutaway",[(s*.315,.045,.943,1,1),(s*.309,.039,.928,.95,.92)],.0078,.008,wardrobe,[glove],steps=8)
    cuff=loft("Glove wrist closure",[[arm_point(z,t,s,.0037) for t in st] for z in [.952,.955,.967,.974]],wardrobe,[glove],caps=False)
    box("Glove strap closure",(s*.329,.033,.967),(.026,.005,.014),.0032,hardware,deep,rot=(0,s*.22,0))
    box("Glove cuff marker",(s*.331,.030,.967),(.007,.0013,.0034),.0005,hardware,steel)

# Local remesh only the underlying shoulder-to-arm junctions. The face,
# clothing and all other objects stay outside this operation.
bpy.ops.object.select_all(action="DESELECT")
for obj in anatomy.objects:
    if obj==torso or obj.name.startswith("Arm "):
        obj.select_set(True)
bpy.context.view_layer.objects.active=torso
bpy.ops.object.join()
torso.data.remesh_voxel_size=.0027
bpy.ops.object.voxel_remesh()
for poly in torso.data.polygons:
    poly.use_smooth=True
if not args.preview:
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(70), island_margin=.004)
    bpy.ops.object.mode_set(mode="OBJECT")
modifier=torso.modifiers.new("Relax local skin surface","SMOOTH")
modifier.factor=.46
modifier.iterations=5

# Relax and fit the shoulder strap bridge to the actual joined shoulder.
bpy.context.view_layer.update()
torso_bvh=BVHTree.FromObject(torso,bpy.context.evaluated_depsgraph_get())
for strap in wardrobe.objects:
    if not strap.name.startswith("Over-shoulder knit strap"):
        continue
    for vert in strap.data.vertices:
        u=(vert.index//11)/42
        blend=math.sin(math.pi*u)**1.55
        if blend>.05:
            x,y,z=vert.co
            hit=torso_bvh.ray_cast(Vector((x,y,1.49)),Vector((0,0,-1)),.20)[0]
            if hit is not None:
                vert.co.z=(1-blend)*z+blend*(hit.z+.0026)

# Back jacket bridge leaves upper shoulders bare. Built as a solidified open panel.
def back_panel(t,f):
    zlo=1.093+.017*(abs(t)/1.58)**2
    zhi=1.232+.035*(abs(t)/1.58)**2-.013*math.cos(t*2)
    z=zlo+(zhi-zlo)*f
    x=(.146+.046*f)*math.sin(t)
    depth=.088+.019*math.sin(math.pi*f)*(1+.20*math.sin(5*t))
    y=.007+depth*math.cos(t)+.040*abs(math.sin(t))+.003*math.sin(6*t+f*9)*math.sin(math.pi*f)
    return (x,y,z)
pv=[back_panel(t,f) for f in np.linspace(0,1,44) for t in np.linspace(-1.65,1.65,93)]
pf=[(j*93+i,j*93+i+1,(j+1)*93+i+1,(j+1)*93+i) for j in range(43) for i in range(92)]
pb=mesh("Dropped cropped jacket back | separate shell",pv,pf,wardrobe,[jacket],[(i/92,j/43) for j in range(44) for i in range(93)])
mod=pb.modifiers.new("Back shell thickness","SOLIDIFY");mod.thickness=.0045
for f in [0,.06,.95,1]:
    pp=[back_panel(t,f) for t in np.linspace(-1.63,1.63,29)]
    line("Back collar binding" if f>.9 else "Back ribbed waistband",pp,[1]*29,wardrobe,deep,.0032 if f>.9 else .005)
for s in [-1,1]:
    line("Back wing insignia",[(0,.113,1.181),(s*.023,.112,1.193),(s*.042,.111,1.205)],
         [.50,1,.08],wardrobe,white,.0039)
    line("Back wing inner slash",[(s*.003,.115,1.168),(s*.021,.113,1.182),(s*.031,.112,1.195)],
         [.20,.90,.12],wardrobe,white,.0025)

# Equipment is modeled off the leggings and can be repositioned independently.
bt=np.linspace(-math.pi,math.pi,112,endpoint=False)
def belt_point(z,t):
    c=min(1,(z-.903)/.118)
    tx,ty,_=torso_point(1.021,t,.005)
    return ((1-c)*.156*math.sin(t)+c*tx+.0045*math.sin(t),
            (1-c)*(-.016-.086*math.cos(t))+c*ty-.0045*math.cos(t),z)
belt=loft("Utility waist belt",[[belt_point(z,t) for t in bt] for z in [.996,1.000,1.018,1.022]],
          hardware,[glove],caps=False)
mod=belt.modifiers.new("Belt leather thickness","SOLIDIFY");mod.thickness=.003
yf=belt_point(1.010,0)[1]-.002
frame=[(-.021,yf,1.000),(.020,yf,1.000),(.020,yf,1.021),(-.021,yf,1.021)]
for i in range(4):
    p1,p2=frame[i],frame[(i+1)%4]
    line("Buckle frame rail",[p1,p2],[1,1],hardware,steel,.0025)
line("Buckle prong",[(-.015,yf-.001,1.011),(.010,yf-.002,1.011)],[1,.66],hardware,steel,.0012)
for s in [-1,1]:
    for f in [-1,1]:
        points=[(s*.075,-.069 if f==-1 else .063,1.018,.92,1),(s*.097,-.081 if f==-1 else .067,.983,1,1),
                (s*.117,-.092 if f==-1 else .064,.945,1,1),(s*.165,-.067 if f==-1 else .042,.904,.86,1)]
        tube("Utility suspension strap",points,.0085,.0017,hardware,[violet],steps=24,segments=10)
        for x,y,z,_,_ in points[:2]:
            box("Strap slide",(x,y+f*.003,z),(.020,.003,.010),.0012,hardware,steel,rot=(0,s*.25,0))
    loc=(s*.167,-.032,.897)
    box(f"Hip utility pouch {s}",loc,(.036,.056,.085),.007,hardware,glove,rot=(0,-s*.13,0))
    box(f"Violet pouch flap {s}",(s*.183,-.038,.915),(.012,.053,.043),.0048,hardware,deep,rot=(0,-s*.13,0))
    box("Pouch clasp",(s*.191,-.039,.904),(.005,.013,.016),.0018,hardware,steel)
    box("Pouch strap tab",(s*.191,-.039,.886),(.004,.009,.019),.0012,hardware,violet)
    for y in [-.059,-.015]:
        line("Case welt stitch",[(s*.187,y,.870),(s*.192,y,.891),(s*.187,y,.921)],[.7,1,.7],hardware,pearl,.00056)
chain=[]
for t in np.linspace(-math.pi,math.pi,56,endpoint=False):
    z=1.354-.049*max(0,math.cos(t))**1.7
    chain.append(torso_point(z,t,.0046))
line("Pendant chain",chain,[1]*len(chain),hardware,steel,.00106,closed=True)
zp=1.300
yp=torso_point(zp,0,.0077)[1]
box("Pendant bezel",(0,yp,zp),(.021,.005,.021),.0020,hardware,steel,rot=(0,math.pi/4,0))
box("Violet pendant enamel",(0,yp-.003,zp),(.016,.005,.016),.0020,hardware,gem,rot=(0,math.pi/4,0))

# Sole profile and bonded shoe overlays are clean surface models. Retain the
# ankle position and reconstruct the original candidate's footprint and toe spring.
# Use an explicitly closed angular outline with a broader radius at the toe.
def shoe_outline(t,s=1):
    x=.046*math.cos(t)*(1+.12*math.sin(t))
    y=-.072-.137*math.sin(t)
    x*=1+.075*math.cos(t)*s
    return x,y
sole_spec=[(.004,.88,.025),(.008,.99,.017),(.016,1.015,.010),(.024,1.025,.006),
           (.033,1.020,.004),(.044,1.02,.003),(.054,1.005,.0015),(.061,.984,0)]
upper_spec=[(.058,.95,-.067,.133),(.069,.96,-.064,.134),(.085,.90,-.058,.127),(.100,.83,-.043,.113),
            (.116,.76,-.022,.092),(.133,.72,-.005,.077),(.150,.70,.000,.065),
            (.167,.68,.006,.051),(.180,.64,.005,.046)]
su=np.linspace(0,2*math.pi,96,endpoint=False)
def upper_point(z,t,s,off=0):
    w,cy,l=sample(upper_spec,z)
    x=shoe_outline(t,s)[0]*w+off*math.cos(t)
    y=cy-(l+off)*math.sin(t)
    return (s*.133+x,y,z)
for s in [-1,1]:
    so=[]
    for z,scale,rise in sole_spec:
        row=[]
        for t in su:
            x,y=shoe_outline(t,s)
            # The ball and heel carry weight. The last few centimeters of the
            # toe roll up into the front bumper.
            toe_rise=.017*max(0,math.sin(t))**8
            row.append((s*.133+x*scale,y*scale,z+toe_rise*(1+rise*8)))
        so.append(row)
    loft(f"Layered rubber and EVA sole {s}",so,sneakers,[rubber,midsole,pearl],
         choose=lambda j,i,n:0 if j<2 else 2 if j==3 else 1)
    upper_rows=[[upper_point(z,t,s) for t in su] for z in np.linspace(.058,.180,52)]
    loft(f"Runner mesh upper {s}",upper_rows,sneakers,[toe,jacket,deep],
         choose=lambda j,i,n:1 if .13<i/n<.39 and j>34 or .64<i/n<.89 else 2 if j>43 else 0)
    for center,span,col in [(0,.67,pearl),(math.pi,.67,pearl),(math.pi*1.5,.59,jacket),(math.pi/2,.75,toe)]:
        vv=[]
        for j in range(23):
            f=j/22
            for k in range(35):
                a=center+(k/17-1)*span
                base=.061+.009*max(0,math.sin(a))**4
                h=(.037 if col==toe else .083 if col==jacket else .052+.019*math.cos(a-center))
                z=base+h*f
                vv.append(upper_point(z,a,s,.0016))
        ff=[(j*35+i,j*35+i+1,(j+1)*35+i+1,(j+1)*35+i) for j in range(22) for i in range(34)]
        mesh("Bonded upper side overlay",vv,ff,sneakers,[col],[(i/34,j/22) for j in range(23) for i in range(35)])
        line("Welded upper panel seam",vv[-35::2],[1]*18,sneakers,deep,.00085)
    seam=[upper_point(.168+.006*(-math.sin(a)),a,s,.0016) for a in su[::3]]
    line("Padded ankle collar",seam,[1]*len(seam),sneakers,deep,.0052,closed=True)
    tongue_rows=[]
    for j,z in enumerate(np.linspace(.102,.189,28)):
        row=[]
        for k in range(21):
            t=math.pi/2+(k/10-1)*.58
            x,y,_=upper_point(min(z,.178),t,s,.0026)
            row.append((x,y-.0008,z-.0045*abs(k/10-1)**2))
        tongue_rows.append(row)
    vv=[v for row in tongue_rows for v in row]
    ff=[(j*21+i,j*21+i+1,(j+1)*21+i+1,(j+1)*21+i) for j in range(27) for i in range(20)]
    tg=mesh("Padded lace tongue",vv,ff,sneakers,[pearl],[(i/20,j/27) for j in range(28) for i in range(21)])
    m=tg.modifiers.new("Tongue lining","SOLIDIFY");m.thickness=.0033
    lace_rows=[]
    for j in range(6):
        z=.104+.011*j
        endpoints=[]
        for a in [math.pi/2-.60,math.pi/2+.60]:
            x,y,zz=upper_point(z,a,s,.004)
            endpoints.append((x,y-.001,zz))
            ellipsoid("Lace eyelet",(x,y-.001,zz),(.0039,.0018,.0039),sneakers,steel,20,10)
        lace_rows.append(endpoints)
    for j in range(5):
        for i in [0,1]:
            a,b=lace_rows[j][i],lace_rows[j+1][1-i]
            mid=(s*.133,min(a[1],b[1])-.009,(a[2]+b[2])/2+.001)
            line("Crossed braided lace",[a,mid,b],[.8,1,.82],sneakers,laces,.00165)
    mid=(s*.133,-.057,.161)
    for dx in [-1,1]:
        line("Tied lace bow",[mid,(mid[0]+dx*.013,mid[1]-.005,mid[2]+.007),
            (mid[0]+dx*.018,mid[1]-.007,mid[2]+.002),mid],[.8,1,.9,.7],sneakers,laces,.00145)
    for j in range(5):
        box("Outsole traction lug",(s*.133,-.157+.043*j,.006),(.061,.013,.010),.0037,sneakers,rubber)
    for y in [.025,.045]:
        box("Heel stabilizer",(s*.133,y,.070),(.056,.017,.024),.005,sneakers,jacket)

# Swept locks with tapering cross sections, UV oriented groove shading and
# distinct bands. Ponytail and fringe are individually editable.
for mat in hair_colors:
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    uv_node=nodes.new("ShaderNodeTexCoord")
    scale_node=nodes.new("ShaderNodeVectorMath")
    scale_node.operation="MULTIPLY"
    scale_node.inputs[1].default_value=(68,3,1)
    links.new(uv_node.outputs["UV"],scale_node.inputs[0])
    texture=nodes.new("ShaderNodeTexNoise")
    texture.inputs["Scale"].default_value=3
    texture.inputs["Detail"].default_value=2.4
    links.new(scale_node.outputs["Vector"],texture.inputs["Vector"])
    bump=nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.22
    bump.inputs["Distance"].default_value=.00020
    links.new(texture.outputs["Fac"],bump.inputs["Height"])
    hair_shader=nodes.get("Principled BSDF")
    hair_shader.inputs["Specular IOR Level"].default_value=.26
    links.new(bump.outputs["Normal"],hair_shader.inputs["Normal"])

def scalp_line(a):
    c=math.cos(a)
    fall=1.562+.125*max(0,c)**.70+.010*math.sin(a*3)**2
    return fall+.013*gauss(a,0,0,0,.32,1)-.008*gauss(abs(a),0,.85,0,.28,1)
sa=np.linspace(-math.pi,math.pi,112,endpoint=False)
scalp=[]
for f in np.linspace(0,1,54):
    row=[]
    for t in sa:
        z=scalp_line(t)+(1.742-scalp_line(t))*f
        x,y,z=face_point(t,z)
        envelope=.0048+.004*math.sin(math.pi*f)**.7
        row.append((x+envelope*math.sin(t),y-envelope*math.cos(t),z+.0038+envelope*f))
    scalp.append(row)
loft("Scalp coverage | center part and controlled hairline",scalp,hair,[hair_colors[0],hair_colors[1]],caps=False,
     choose=lambda j,i,n: int((i//9)%5==0))
tiet=[]
for t in np.linspace(0,2*math.pi,32,endpoint=False):
    tiet.append((.035*math.cos(t),.097+.018*math.sin(t),1.725+.022*math.sin(t)))
line("Violet ponytail tie",tiet,[1]*len(tiet),hair,violet,.0050,closed=True)

# Espressso underlayer, primary silhouette locks, then selective brighter ribbons.
pony_core=[(0,.083,1.714,1,1),(.009,.131,1.759,1.12,1.12),
           (.010,.168,1.729,1.27,1.13),(-.008,.179,1.647,1.45,1.15),
           (-.010,.164,1.568,1.19,.92),(.015,.153,1.501,.83,.65),
           (.025,.159,1.408,.64,.56),(.018,.120,1.345,.043,.05)]
tube("Ponytail | primary core",pony_core,.032,.025,hair,[hair_colors[0]],steps=81,segments=34)
for j in range(24):
    a=2*math.pi*j/24
    pts=[]
    for k,(x,y,z,w,d) in enumerate(pony_core):
        phase=a+.24*math.sin(k*1.09)
        f=(.72+.27*math.sin(k*1.2+j))*(1-.048*k)
        dx=math.cos(phase)*.040*w*f
        dy=math.sin(phase)*.040*d*f
        pts.append((x+dx+.009*math.sin(j+k*1.8),y+dy,z+(.013*math.sin(a)*k/7),
                    max(.03,w*(.62+.19*math.cos(j+k))),max(.03,d*(.63+.20*math.sin(j+k)))))
    m0=4 if j in [8,9,10] else rng.choice([0,0,1,1,2,3])
    m1=5 if m0==4 else (2 if m0==0 else m0)
    tube(f"Ponytail | flowing lock {j+1:02d}",pts,.017,.0108,hair,[hair_colors[m0],hair_colors[m1]],
         steps=81,segments=16,slots=lambda j,i,n: int(i in [3,4] and 10<j<68))
# Crown flow curves follow scalp toward the ponytail root.
for j in range(34):
    a=-math.pi+2*math.pi*(j+.5)/34+.024*math.sin(j*1.5)
    if abs(a)<.65:
        continue
    pts=[]
    for k in range(7):
        f=k/6
        t=a+(1 if a<0 else -1)*.35*math.sin(math.pi*f)
        z=scalp_line(t)+(1.732-scalp_line(t))*f**.82
        x,y,z=face_point(t,z)
        co=(x+(.006+.003*math.sin(math.pi*f))*math.sin(t),
            y-(.0033+.0052*math.sin(math.pi*f)**.52)*math.cos(t), z+.0020+.0065*f)
        pts.append((*co,.24+.83*math.sin(math.pi*f),.24+.83*math.sin(math.pi*f)))
    tube(f"Crown sweep {j+1:02d}",pts,.010,.0020,hair,[hair_colors[rng.choice([0,0,1,1,2])]],
         steps=31,segments=12)
for s in [-1,1]:
    for j in range(7):
        d=(j-3.0)*.0033
        pos=[
            (s*(.009+.003*j),-.069+d*.22,1.716-j*.0012,.18,.32),
            (s*(.033+d),-.094-d*.27,1.694+d*.35,1.1,1.1),
            (s*(.053+d),-.086-d*.48,1.661+d*.18,1.04,1.04),
            (s*(.070+d),-.064-d*.47,1.627,1,.96),
            (s*(.076+d*.7),-.053-d*.21,1.598-.001*j,.78,.80),
            (s*(.067+d*.54),-.059+d*.59,1.572-.0032*j,.47,.55),
            (s*(.049+d*.88),-.058+d*.32,1.548-.0075*j,.036,.065)]
        tube(f"{'Left' if s>0 else 'Right'} face framing lock {j+1:02d}",pos,
             .0087,.0057,hair,[hair_colors[rng.choice([0,1,2,3])]], steps=51,segments=14)

# The accent follows the outer left curve of the tail, staying visible
# around the crown in the head-on silhouette.
for j in range(4):
    d=j*.0033
    tube("Violet crown-to-ponytail accent", [
        (-.021,.121+d,1.742, .35,.58),(-.036-d,.137,1.755,1,1),
        (-.055-d,.140,1.715,.91,.9),(-.062-d,.146,1.664,.68,.75),
        (-.058-d,.154,1.612,.35,.48),(-.060-d,.156,1.570,.08,.12),
    ],.0073,.0048,hair,[hair_colors[4+(j==1)]],steps=55,segments=12)
for s in [-1,1]:
    for j in range(5):
        d=j*.0016
        points=[(s*(.041+d),-.086,1.687),(s*(.058+d),-.086-d,1.645),
                (s*(.077+d),-.055,1.605),(s*(.073+d),-.053,1.579-d*2),
                (s*(.059+d),-.069,1.548-d*3)]
        line("Loose temple strand",points,[.7,1,.83,.39,.045],hair,hair_colors[j%3],.00062)

# Sparse alpha cards trace flyaways. The texture is procedurally rasterized
# from individual tapered fibers and packed into the master.
w,h=64,256
x=np.linspace(0,1,w)[None,:]
y=np.linspace(0,1,h)[:,None]
alpha=np.zeros((h,w))
for u in [.21,.30,.39,.46,.56,.62,.75]:
    center=.5+(u-.5)*(1-.6*y)+.035*np.sin(y*6+u*4)
    strand=np.exp(-((x-center)/(.012+.005*np.sin(y*4)**2))**2)
    alpha=np.maximum(alpha,strand*(1-y**1.7)**.65)
rgba=np.empty((h,w,4),dtype=np.float32)
rgba[:,:,:3]=(.19,.11,.10)
rgba[:,:,3]=alpha
card_image=save_map("hair-fibers",rgba)
cardmat=material("Hair | thin strand cards", "352225", .42, coat=.12)
ntree=cardmat.node_tree
img=ntree.nodes.new("ShaderNodeTexImage")
img.image=card_image
bs=ntree.nodes.get("Principled BSDF")
ntree.links.new(img.outputs["Color"],bs.inputs["Base Color"])
ntree.links.new(img.outputs["Alpha"],bs.inputs["Alpha"])
for j in range(14):
    a=2*math.pi*j/14
    pts=[]
    for k,(xx,yy,zz,sx,sy) in enumerate(pony_core[2:]):
        dx=.052*sx*math.cos(a+k*.18)
        dy=.044*sy*math.sin(a+k*.18)
        pts.append((k,xx+dx,yy+dy,zz+.008*math.sin(a)*k))
    cv=[];cf=[]
    for k,t in enumerate(np.linspace(0,len(pts)-1,37)):
        co=np.array(sample(pts,t))
        for s in [-1,1]:
            p=co.copy()
            p[0]+=s*.0028*(.5+.5*math.sin(math.pi*k/36))
            cv.append(tuple(p))
    cf=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(36)]
    mesh(f"Ponytail edge flyaway card {j+1:02d}",cv,cf,hair,[cardmat],[(i,k/36) for k in range(37) for i in [0,1]])

# Shorten the neck in the existing world frame without a seam under the jaw.
bpy.context.view_layer.update()
def proportion_z(z):
    return .013*math.exp(-((z-1.559)/.052)**4)
for obj in face.objects:
    world=obj.matrix_world.copy()
    inv=world.inverted()
    if obj.type=="MESH":
        for vert in obj.data.vertices:
            co=world@vert.co
            co.z+=proportion_z(co.z)
            vert.co=inv@co
    else:
        for spline in obj.data.splines:
            for point in spline.bezier_points:
                co=world@point.co
                co.z+=proportion_z(co.z)
                point.co=inv@co
    obj.location.z-=.041
for obj in hair.objects:
    obj.location.z-=.036
for vert in torso.data.vertices:
    f=min(1,max(0,(vert.co.z-1.36)/.18))
    vert.co.z-=.043*f*f
    if vert.co.z<1.025 and abs(vert.co.x)<.18:
        tuck=max(0,min(1,(1.025-vert.co.z)/.01))
        vert.co.x*=1-.12*tuck
        vert.co.y*=1-.12*tuck
# Pack the strand texture with the face and torso assets.
card_image.filepath="//textures/hair-fibers.png"

# Sample a knitted height field into a periodic tangent-space normal tile.
# This gives the cloth assets reusable microstructure apart from Blender noise.
px,py=np.meshgrid(np.arange(512)/512,np.arange(512)/512)
height=.5*np.cos(2*math.pi*13*px)*np.sin(2*math.pi*(13*py+2*px))+.25*np.sin(2*math.pi*26*py)
du=(np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*.22
dv=(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*.22
norm=np.stack((-du,-dv,np.ones_like(du)),axis=-1)
norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
tile=np.ones((512,512,4),dtype=np.float32)
tile[:,:,:3]=norm*.5+.5
knit=save_map("technical-knit-normal",tile,data=True)
for mat in [graphite,top,violet,deep,jacket,white,toe,laces]:
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    bs=nodes.get("Principled BSDF")
    coords=nodes.new("ShaderNodeTexCoord")
    repeat=nodes.new("ShaderNodeMapping")
    repeat.inputs["Scale"].default_value=(12,12,1)
    links.new(coords.outputs["UV"],repeat.inputs["Vector"])
    img=nodes.new("ShaderNodeTexImage")
    img.image=knit
    links.new(repeat.outputs["Vector"],img.inputs["Vector"])
    normal=nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value=.39
    links.new(img.outputs["Color"],normal.inputs["Color"])
    links.new(normal.outputs["Normal"],bs.inputs["Normal"])

def bake_face_tint():
    scene.render.engine="CYCLES"
    scene.cycles.samples=1
    ntree=skin_face.node_tree
    bs=ntree.nodes.get("Principled BSDF")
    out=ntree.nodes.get("Material Output")
    emit=ntree.nodes.new("ShaderNodeEmission")
    ntree.links.new(attr.outputs["Color"],emit.inputs["Color"])
    ntree.links.new(emit.outputs[0],out.inputs["Surface"])
    image=bpy.data.images.new("face-albedo-baked",width=2048,height=1024,alpha=True)
    target=ntree.nodes.new("ShaderNodeTexImage")
    target.image=image
    target.select=True
    ntree.nodes.active=target
    bpy.ops.object.select_all(action="DESELECT")
    head.select_set(True)
    bpy.context.view_layer.objects.active=head
    bpy.ops.object.bake(type="EMIT",margin=8)
    image.filepath_raw=str(TEXTURES/"face-albedo-baked.png")
    image.file_format="PNG"
    image.save()
    image.pack()
    image.filepath="//textures/face-albedo-baked.png"
    ntree.links.new(bs.outputs[0],out.inputs["Surface"])
    ntree.nodes.remove(emit)
    target.label="Baked face tint for export | editable tint remains connected"
    return image

if not args.preview:
    bake_face_tint()

# The review scene reuses the original lighting and comparison camera. Face,
# clay and gameplay presets are all retained as actual camera objects.
def aim(ob,target):
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()

presets={
    "front":((0,-4,1),(0,0,.89),2.04),
    "rear":((0,4,1),(0,0,.89),2.04),
    "side":((-4,0,1),(0,0,.89),2.04),
    "three-quarter":((2.7,-4,1.5),(0,0,.89),2.04),
    "face":((.10,-4,1.61),(0,-.025,1.575),.422),
    "face-three-quarter":((1.8,-4,1.64),(0,-.025,1.572),.411),
    "clay":((2.7,-4,1.5),(0,0,.89),2.04),
    "selection":((1.8,-4,1.26),(0,0,.91),1.96),
    "gameplay":((0,5.4,2.25),(0,0,.93),5.85),
}
cameras=collection("07 | Render cameras")
for key,(loc,target,scale) in presets.items():
    data=bpy.data.cameras.new(key)
    data.type="ORTHO"
    data.ortho_scale=scale
    camera=bpy.data.objects.new(f"Camera | {key}",data)
    cameras.objects.link(camera)
    camera.location=loc
    aim(camera,target)
clay=material("Reconstruction clay", "B9B1B0", .65)
bpy.data.objects["Studio floor"].location.z=.00085
scene.render.engine="CYCLES"
scene.cycles.use_denoising=True
scene.cycles.samples=24 if args.preview else 48
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.view_settings.view_transform="AgX"
scene.camera=bpy.data.objects["Camera | three-quarter"]
scene.render.resolution_x=1100
scene.render.resolution_y=1400
render_folder=(preview_root or HERE)/"renders"
render_folder.mkdir(exist_ok=True)
if not args.preview:
    scene.render.filepath="//renders/three-quarter.png"
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/"NYRA_Candidate_A_Reconstructed.blend"),compress=True)
    deps=bpy.context.evaluated_depsgraph_get()
    stats=[]
    for group in [anatomy,face,hair,wardrobe,hardware,sneakers]:
        counts={"vertices":0,"triangles":0}
        for obj in group.objects:
            evaluated=obj.evaluated_get(deps)
            data=evaluated.to_mesh()
            if data is not None:
                counts["vertices"]+=len(data.vertices)
                counts["triangles"]+=sum(len(f.vertices)-2 for f in data.polygons)
                evaluated.to_mesh_clear()
        stats.append({"collection":group.name,"objects":len(group.objects),**counts})
    (HERE/"mesh-statistics.json").write_text(json.dumps(stats,indent=2)+"\n")

names=["face","face-three-quarter","three-quarter","front","side","rear"] if args.preview else list(presets)
for name in names:
    scene.camera=bpy.data.objects[f"Camera | {name}"]
    scene.render.resolution_x=600 if args.preview else 1100
    scene.render.resolution_y=760 if args.preview else 1400
    if name in ["face","face-three-quarter"] and not args.preview:
        scene.render.resolution_x=1250
        scene.render.resolution_y=1590
    if name=="gameplay":
        scene.render.resolution_x,scene.render.resolution_y=1280,720
        for light in [ob for ob in scene.objects if ob.type=="LIGHT"]:
            light.hide_render=True
        scene.world.node_tree.nodes["Background"].inputs[1].default_value=.55
        for label,loc,color,power in [
            ("Metro sun",(24,-18,42),(1,.98,.918),1.45),
            ("Metro fill",(-24,22,32),(.627,.769,.910),.95),
        ]:
            data=bpy.data.lights.new(label,"SUN")
            data.color=color
            data.energy=power
            ob=bpy.data.objects.new(label,data)
            scene.collection.objects.link(ob)
            ob.location=loc
            aim(ob,(0,0,.9))
    scene.view_layers[0].material_override=clay if name=="clay" else None
    scene.render.filepath=str(render_folder/f"{name}.png")
    bpy.ops.render.render(write_still=True)
