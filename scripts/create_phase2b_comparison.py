from PIL import Image, ImageDraw, ImageFont

def make_phase2b_matched_comparison():
    # 1. Matched comparison: Phase 2B Front vs Approved NYRA Reference Portrait
    img_proto = Image.open("production_v3/prototype/renders/nyra_phase2b_front.png")
    img_ref = Image.open("references/turnarounds/nyra_portrait_face.jpg")

    w, h = 1024, 1024
    img_proto = img_proto.resize((w, h), Image.Resampling.LANCZOS)

    # Crop reference to match the square 1024x1024 framing
    rw, rh = img_ref.size
    min_dim = min(rw, rh)
    crop_x = (rw - min_dim) // 2
    crop_y = int((rh - min_dim) * 0.12)
    img_ref_crop = img_ref.crop((crop_x, crop_y, crop_x + min_dim, crop_y + min_dim)).resize((w, h), Image.Resampling.LANCZOS)

    banner_h = 76
    canvas = Image.new("RGB", (w * 2, h + banner_h), (18, 18, 22))
    canvas.paste(img_proto, (0, banner_h))
    canvas.paste(img_ref_crop, (w, banner_h))

    draw = ImageDraw.Draw(canvas)
    labels = [
        ("PHASE 2B PROTOTYPE: CC0 Sculpt + Eye/Skin/Hair Proxy", 0),
        ("TARGET: Approved NYRA Visual Reference Portrait", w)
    ]
    for text, x_off in labels:
        draw.rectangle([x_off, 0, x_off + w - 2, banner_h], fill=(28, 28, 34))
        draw.text((x_off + 30, 26), text, fill=(240, 240, 245))
        draw.line([(x_off, 0), (x_off, h + banner_h)], fill=(60, 60, 70), width=2)

    out_matched = "production_v3/prototype/renders/comparison_phase2b_vs_reference.png"
    canvas.save(out_matched, quality=95)
    print(f"Saved: {out_matched}")

    # 2. Complete Phase 2B Turnaround Sheet: Front, 3/4, Side, plus Target Reference
    img_34 = Image.open("production_v3/prototype/renders/nyra_phase2b_threequarter.png").resize((w, h), Image.Resampling.LANCZOS)
    img_side = Image.open("production_v3/prototype/renders/nyra_phase2b_side.png").resize((w, h), Image.Resampling.LANCZOS)

    canvas4 = Image.new("RGB", (w * 4, h + banner_h), (18, 18, 22))
    canvas4.paste(img_proto, (0, banner_h))
    canvas4.paste(img_34, (w, banner_h))
    canvas4.paste(img_side, (w * 2, banner_h))
    canvas4.paste(img_ref_crop, (w * 3, banner_h))

    draw4 = ImageDraw.Draw(canvas4)
    labels4 = [
        ("Phase 2B — Front View", 0),
        ("Phase 2B — Three-Quarter View", w),
        ("Phase 2B — Side Profile", w * 2),
        ("Approved NYRA Reference Portrait", w * 3)
    ]
    for text, x_off in labels4:
        draw4.rectangle([x_off, 0, x_off + w - 2, banner_h], fill=(28, 28, 34))
        draw4.text((x_off + 30, 26), text, fill=(240, 240, 245))
        draw4.line([(x_off, 0), (x_off, h + banner_h)], fill=(60, 60, 70), width=2)

    out_turnaround = "production_v3/prototype/renders/nyra_phase2b_turnaround_sheet.png"
    canvas4.save(out_turnaround, quality=95)
    print(f"Saved: {out_turnaround}")

if __name__ == "__main__":
    make_phase2b_matched_comparison()
