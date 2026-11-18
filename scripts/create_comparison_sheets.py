from PIL import Image, ImageDraw, ImageFont

def make_front_comparison():
    img_base = Image.open("production_v3/prototype/renders/baseline_female_head_front.png")
    img_proto = Image.open("production_v3/prototype/renders/nyra_prototype_head_front.png")
    img_ref = Image.open("references/turnarounds/nyra_portrait_face.jpg")

    # Resize all to 1024x1024
    w, h = 1024, 1024
    img_base = img_base.resize((w, h), Image.Resampling.LANCZOS)
    img_proto = img_proto.resize((w, h), Image.Resampling.LANCZOS)
    
    # Crop ref to center square bust
    rw, rh = img_ref.size
    min_dim = min(rw, rh)
    crop_x = (rw - min_dim) // 2
    crop_y = int((rh - min_dim) * 0.15)
    img_ref_crop = img_ref.crop((crop_x, crop_y, crop_x + min_dim, crop_y + min_dim)).resize((w, h), Image.Resampling.LANCZOS)

    # Composite canvas: 3072 x 1100 (extra 76px for banner)
    banner_h = 76
    canvas = Image.new("RGB", (w * 3, h + banner_h), (18, 18, 22))

    # Paste panels
    canvas.paste(img_base, (0, banner_h))
    canvas.paste(img_proto, (w, banner_h))
    canvas.paste(img_ref_crop, (w * 2, banner_h))

    draw = ImageDraw.Draw(canvas)
    # Header labels
    # Use default font
    labels = [
        ("1. BASELINE: Blender CC0 Realistic Female", 0),
        ("2. PROTOTYPE: NYRA Sculpted CC0 Base", w),
        ("3. TARGET: Approved NYRA Visual Reference", w * 2)
    ]
    for text, x_off in labels:
        draw.rectangle([x_off, 0, x_off + w - 2, banner_h], fill=(28, 28, 34))
        draw.text((x_off + 30, 26), text, fill=(240, 240, 245))
        # Divider line
        draw.line([(x_off, 0), (x_off, h + banner_h)], fill=(60, 60, 70), width=2)

    out_path = "production_v3/prototype/renders/comparison_front_baseline_vs_prototype_vs_reference.png"
    canvas.save(out_path, quality=95)
    print(f"Saved: {out_path}")

def make_turnaround_comparison():
    img_front = Image.open("production_v3/prototype/renders/nyra_prototype_head_front.png")
    img_34 = Image.open("production_v3/prototype/renders/nyra_prototype_head_threequarter.png")
    img_side = Image.open("production_v3/prototype/renders/nyra_prototype_head_side.png")

    w, h = 1024, 1024
    banner_h = 76
    canvas = Image.new("RGB", (w * 3, h + banner_h), (18, 18, 22))

    canvas.paste(img_front, (0, banner_h))
    canvas.paste(img_34, (w, banner_h))
    canvas.paste(img_side, (w * 2, banner_h))

    draw = ImageDraw.Draw(canvas)
    labels = [
        ("NYRA CC0 Prototype — Front View", 0),
        ("NYRA CC0 Prototype — Three-Quarter View", w),
        ("NYRA CC0 Prototype — Left Profile View", w * 2)
    ]
    for text, x_off in labels:
        draw.rectangle([x_off, 0, x_off + w - 2, banner_h], fill=(28, 28, 34))
        draw.text((x_off + 30, 26), text, fill=(240, 240, 245))
        draw.line([(x_off, 0), (x_off, h + banner_h)], fill=(60, 60, 70), width=2)

    out_path = "production_v3/prototype/renders/comparison_turnaround_prototype.png"
    canvas.save(out_path, quality=95)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    make_front_comparison()
    make_turnaround_comparison()
