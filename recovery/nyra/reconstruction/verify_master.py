"""Verify the packed production scene and report the construction boundaries."""
import hashlib
import json
from pathlib import Path

import bmesh
import bpy

root = Path(__file__).resolve().parent
source_folder = root.parent / "candidates/candidate-a"
checkpoints = {
    "nyra-a.glb": "862f8105ecb861efc3d959dc81762c4fc6c5ee0016052795bb42d262d60c0f5d",
    "renders/original/nyra-review.blend": "f14150d876a8ea595316f65db7ab7fe8c090b1b3c27440ceeec99fbc7e11393a",
}
for name, expected in checkpoints.items():
    with (source_folder/name).open("rb") as original:
        assert hashlib.file_digest(original, "sha256").hexdigest() == expected, name
bpy.ops.wm.open_mainfile(filepath=str(root/"NYRA_Candidate_A_Reconstructed.blend"))
archive = bpy.data.objects["Candidate A | original atlas and surface"]
assert archive.hide_render
assert len(archive.data.polygons) == 958378
assert not any(obj.type == "ARMATURE" for obj in bpy.context.scene.objects)
images = {im.name: list(im.size) for im in bpy.data.images if im.packed_file}
for name in ["face-albedo-baked", "eye-brown-pigment", "technical-knit-normal", "hair-fibers", "Image_0", "Image_1"]:
    assert name in images, name

def inspect(obj, evaluated=False):
    item = obj
    if evaluated:
        item = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        data = item.to_mesh()
    else:
        data = item.data
    edit = bmesh.new()
    edit.from_mesh(data)
    information = {
        "object": obj.name,
        "evaluated": evaluated,
        "vertices": len(edit.verts),
        "faces": len(edit.faces),
        "uv_layers": len(data.uv_layers),
        "boundary_edges": sum(edge.is_boundary for edge in edit.edges),
        "edges_shared_by_more_than_two_faces": sum(len(edge.link_faces)>2 for edge in edit.edges),
        "loose_vertices": sum(not vert.link_edges for vert in edit.verts),
        "zero_area_faces": sum(face.calc_area()<1e-13 for face in edit.faces),
    }
    edit.free()
    if evaluated:
        item.to_mesh_clear()
    return information

targets = ["Torso and neck | independent skin", "Face | rebuilt orbital loops and sculpted planes",
           "Candidate A fitted leggings | stitched leg and pelvis loops", "Ponytail | primary core",
           "Black athletic crop top | independent shell", "Dropped cropped jacket back | separate shell",
           "Runner mesh upper -1", "Runner mesh upper 1", "Layered rubber and EVA sole -1",
           "Layered rubber and EVA sole 1"]
surfaces = [inspect(bpy.data.objects[name],evaluated=True) for name in targets]
assert surfaces[0]["uv_layers"] > 0, "Skin UV was not saved"
assert all(s["edges_shared_by_more_than_two_faces"] == 0 and s["zero_area_faces"] == 0
           for s in surfaces)
floor_z=bpy.data.objects["Studio floor"].location.z
lug_bottoms=[min((obj.matrix_world @ vert.co).z for vert in obj.data.vertices)
             for obj in bpy.data.objects if obj.name.startswith("Outsole traction lug")]
assert len(lug_bottoms) == 10 and max(abs(z-floor_z) for z in lug_bottoms)<.001
report = {"source_hashes_preserved": checkpoints, "packed_images": images,
          "floor_z_m": floor_z, "traction_lug_clearance_mm": [round((z-floor_z)*1000,3) for z in lug_bottoms],
          "render_cameras": sorted(o.name for o in bpy.context.scene.objects if o.type=="CAMERA"),
          "working_surfaces": surfaces}
(root/"master-verification.json").write_text(json.dumps(report,indent=2)+"\n")
print("VERDICT: PASS — master reopened, source hashes matched and all expected images packed")
for surface in surfaces:
    print(surface)
