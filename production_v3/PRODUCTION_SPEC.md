# NYRA 2.0 — Production Character Specification
**Document ID:** `NYRA-SPEC-V3`  
**Status:** APPROVED DESIGN FREEZE (PHASE 0)  
**Target Engine:** Three.js 0.187+ (WebGL 2.0 / WebGPU)  
**Author:** Technical Art & Art Direction  
**Date:** 18 November 2026  

---

## 1. Executive Summary & Design Authority

This document defines the definitive, authoritative production specification for the **NYRA** hero character for *Metro Runner 3D*. 

All previous procedural generation experiments (Candidate A, Pixal3D neural reconstructions, automated remeshing scripts) are permanently deprecated as primary geometry. Candidate A is preserved strictly as an anatomical and spatial reference point. 

The visual source of truth is established by the locked reference package:
- Primary Master Authority: `recovery/nyra/approved-concept.png`
- Detailed Turnaround References:
  - Front Orthogonal Turnaround: `references/turnarounds/nyra_turnaround_front.jpg`
  - Rear Orthogonal Turnaround: `references/turnarounds/nyra_turnaround_rear.jpg`
  - Left Profile Turnaround: `references/turnarounds/nyra_turnaround_profile.jpg`
  - High-Resolution Head & Bust Portrait: `references/turnarounds/nyra_portrait_face.jpg`
  - Full Phase 3 Concept Sheet: `references/turnarounds/nyra_phase3_predicted_sheet.jpg`

```
+-------------------------------------------------------------------------------+
|                             DESIGN FREEZE NOTICE                              |
| No further generative AI image or mesh generation will be accepted.          |
| All subsequent production passes (mesh acquisition, retopology, sculpting,    |
| texturing, rigging, and engine integration) must strictly conform to the      |
| dimensional, anatomical, chromatic, and performance criteria below.          |
+-------------------------------------------------------------------------------+
```

---

## 2. Character Identity, Anatomy & Proportions

### 2.1 Demographics & Demeanor
- **Name:** NYRA
- **Archetype:** Urban Velocity / High-Agility Parkour Runner
- **Visual Age:** 24–26 years old (mature adult woman; zero juvenile or chibi stylization)
- **Demeanor:** Confident, focused, athletic, self-possessed, lightly mischievous

### 2.2 Proportions & Silhouette
- **Total Height:** 174 cm (in sneakers), calibrated to 1.74 units in Three.js (+Y up).
- **Head Proportion:** Approximately 7.4 to 7.5 heads tall.
- **Physical Build:** Athletic, mesomorphic-lean. Clearly developed musculature suited for sprinting and vaulting:
  - Shoulders: Broad, defined deltoids framing an athletic clavicle.
  - Torso: Toned core with visible linea alba and natural rectus abdominis contours. Smooth lateral waistline; natural ribcage curvature without extreme hourglass distortion.
  - Abdominal Plane: Continuous, organic abdominal contour from underbust to navel. **STRICT REQUIREMENT:** Absolute elimination of any horizontal shelf, ridge, or extrusion underneath the sports bra.
  - Lower Body: Powerful, athletic quadriceps, defined hamstrings, and toned calves tapering to slender ankles.
  - Gluteus: Athletic, lifted volume balanced naturally above the hamstring insertion.

### 2.3 Craniofacial Architecture & Features
- **Facial Shape:** Harmonious oval with softly squared, defined jaw angles and a sculpted chin. High, well-defined zygomatic arches (cheekbones).
- **Eyes:**
  - Shape: Expressive almond aperture, slight outer canthal tilt.
  - Iris Color: Warm hazel/golden brown with a dark limbal ring.
  - Detailing: Defined natural double eyelid crease, subtle winged black eyeliner along the upper lash line, fine individual eyelashes.
- **Eyebrows:** Medium-full, dark espresso brown (`#1C1613`), softly arched with individual hair fiber definition toward the tail.
- **Nose:** Straight nasal dorsum, delicate refined tip with subtle supratip break, narrow natural alar base.
- **Lips:** Full, natural rose/mauve lips (`#AC5A63` base with satin gloss) with a pronounced Cupid's bow and realistic lip vermilion texture.
- **Skin & Complexion:**
  - Undertone: Warm medium-golden olive tone.
  - Surface: Subtle micro-porosity, healthy satin sheen over highlight zones (cheekbones, nose bridge, forehead).
  - Accents: Natural peach/rose blush across the cheeks; subtle, fine sun-freckles across the nose bridge and upper cheeks.

---

## 3. Hairstyle & Secondary Dynamic Elements

### 3.1 Hairstyle Architecture
- **Base Style:** High voluminous wavy ponytail originating at the upper crown of the cranium.
- **Ponytail Volume:** Natural undulating wave pattern (S-curves), medium-heavy body.
- **Length:** Extends down to the mid-shoulder blades (~40 cm from crown). Carefully calibrated to clear the stand of the jacket collar and prevent geometry penetration during running cycles.
- **Coloration:**
  - Primary Base: Deep espresso / soft black (`#181416`).
  - Distinctive Accent Streak: An electric vibrant purple / magenta highlight (`#9327E0` to `#A838F5`) running prominently along the outer left quadrant of the ponytail from the binding to the tips.
- **Hair Tie:** High-tension elastic band in vibrant violet (`#8B25D6`) positioned firmly at the ponytail root.
- **Fringe & Face-Framing Tendrils:**
  - Soft, natural parting slightly off-center.
  - Long, delicate tendrils flowing past both temples, brushing the cheekbones and framing the jawline.
  - Subtle wisps at the nape and behind the ears.

### 3.2 Dynamic & Physics Requirements
- The ponytail must be rigged with a 4-bone dynamic chain (`Hair_Ponytail_01` through `Hair_Ponytail_04`) to support real-time inertia/spring physics in Three.js.
- Root placement must have adequate clearance (+3 cm) from the rear neck/jacket collar to prevent clipping in default idle and run states.

---

## 4. Wardrobe & Technical Apparel Specification

```
+-------------------------------------------------------------------------------------------------------+
| NYRA COLOR PALETTE MATRIX                                                                            |
+--------------------+-----------------------+------------+---------------------------------------------+
| Element            | Name                  | Hex Code   | Material Finish / Shader Target             |
+--------------------+-----------------------+------------+---------------------------------------------+
| Jacket Outer       | Royal Midnight Violet | #381254    | Technical semi-gloss nylon / ripstop PBR   |
| Jacket Accent      | Electric Ultraviolet  | #8F2BD9    | Vibrant dyed synthetic / embroidery         |
| Jacket Contrast    | Pure Chalk White      | #F2F2F5    | Matte woven synthetic insert                |
| Sports Bra Base    | Matte Obsidian Black  | #151417    | Performance stretch spandex (roughness 0.7) |
| Bra Piping         | Cyber Amethyst        | #9E37EA    | Elastic bound piping / heat-transfer vinyl  |
| Leggings Base      | Technical Charcoal    | #19181C    | Compression poly-spandex weave              |
| Leggings Chevron   | Violet Kinetic Arc    | #8822D6    | Screen-printed athletic flex rubber         |
| Leggings Stripe    | Crisp White Pinstripe | #FFFFFF    | Heat-pressed reflective lateral piping      |
| Belts & Harness    | Tactical Webbing      | #100F12    | Heavy ballistic nylon (roughness 0.85)      |
| Hardware & Buckles | Brushed Chromium      | #C8CCD0    | Anodized metallic (metallic 0.9, rough 0.2) |
| Sneaker Midsole    | Sculpted White Foam   | #F5F5FA    | Dual-density molded EVA foam                |
| Sneaker Accents    | Amethyst Purple       | #7E1CC7    | Synthetic patent / molded TPU shank         |
| Jewelry Gemstone   | Luminescent Amethyst  | #A242F0    | Translucent cabochon with inner refractor   |
+--------------------+-----------------------+------------+---------------------------------------------+
```

### 4.1 Cropped Off-Shoulder Track Jacket
- **Cut & Silhouette:** Cropped bomber/windbreaker silhouette worn dropped casually below the acromion (off-the-shoulders), completely exposing the clavicles and sports bra straps.
- **Collar:** Fold-down wide collar resting naturally behind the nape and off the upper arms.
- **Sleeves:**
  - Loose, relaxed upper volume tapering into snug ribbed cuffs positioned at the mid-forearm (leaving wrists and forearms bare).
  - Contrasting wide white racing stripe panel running down the outer lateral length of both sleeves.
  - Left sleeve features a small white stylized geometric logo emblem.
- **Rear Graphics:** Stylized geometric winged insignia (white screen-print `#F2F2F5`) centered across the upper shoulder blades.
- **Hardware:** Exposed metal teeth on front opening zipper with a pull tab hanging freely on the wearer's right.

### 4.2 Fitted Performance Sports Bra
- **Cut:** Ergonomic high-impact athletic crop top / racerback silhouette.
- **Neckline:** Moderate V-neckline bounded by vibrant electric purple edge piping.
- **Underbust Band:** Wide, non-slip compression band in obsidian black with a subtle purple accent strip along the bottom seam.
- **Center Detail:** Small triangular notch / keyhole cutout at the sternum with a micro emblem.
- **Fabric Detail:** Breathable micro-mesh jacquard texture on upper bust panels; matte compression weave on lower panels.

### 4.3 High-Waisted Athletic Running Leggings
- **Waistband:** High-rise ergonomic waistband sitting comfortably at the natural waistline just beneath the tactical belt.
- **Panel Architecture:**
  - Primary Base: Deep technical charcoal-black compression fabric.
  - Dynamic Chevrons: Sweeping vibrant purple curvilinear bands starting at the outer hip, curving down across the anterior thigh, and tapering toward the medial knee.
  - Glute Seaming: Anatomical heart-shaped curved contour yoke across the posterior pelvis for enhanced silhouette readability from the third-person gameplay camera.
  - Lateral Racing Stripe: Continuous 8 mm crisp white stripe running vertically along the outer seam from the mid-thigh down to the ankle hem.
- **Ankle Hem:** Clean 7/8 length crop terminating just above the malleoli (ankle bones), leaving a 2 cm skin reveal above the sneaker collar.

### 4.4 Tactical Utility Belt & Harness System
- **Belt:** 38 mm ballistic nylon tactical belt with a brushed chrome square prong buckle centered at the waist.
- **Right Hip Pouch:** Structured rectangular utility pouch (12 cm x 8 cm x 4 cm) in deep purple/black with a fold-over magnetic flap and silver metallic rivet snap.
- **Left Hip Pouch:** Vertical cylindrical canister / tech cartridge holster (10 cm x 4 cm) secured by a silver retention bracket.
- **Leg Holster Straps:** Purple nylon harness straps extending diagonally from the belt rings down around the lateral thighs with silver adjusters.

### 4.5 Fingerless Tactical Gloves
- **Type:** Half-finger precision running gloves ending at the proximal interphalangeal joints.
- **Material:** Matte black synthetic leather palms, breathable perforated backhand fabric.
- **Accents:** Padded knuckle reinforcement ridges; adjustable wrist wrap with Velcro closure.

### 4.6 Chunky High-Top Running Sneakers
- **Silhouette:** Modern chunky urban runner / maximalist sneaker silhouette with aggressive ergonomic stance.
- **Sole Architecture:**
  - Thick, sculpted multi-density EVA midsole (45 mm heel stack, 25 mm forefoot stack) in chalk white.
  - Integrated purple TPU torsion shank in the midfoot arch.
  - Segmented outsole with deep purple rubber traction pods.
- **Upper Construction:**
  - Mixed-media upper combining breathable black mesh, white leather mudguards, and royal purple heel cup reinforcements.
  - Ghillie lacing system with vibrant purple round athletic laces.
  - Padded high-top collar with heel pull-tab in bright violet.

### 4.7 Accessories & Jewelry
- **Earrings:** Medium circular silver hoop earrings (30 mm diameter, 2 mm wire gauge) through the lobe of both ears. Polished chrome metallic shader.
- **Necklace:** Fine gunmetal link chain supporting a kite-shaped/diamond silver pendant containing a luminous purple cabochon gemstone resting on the upper sternum.

---

## 5. Technical Budgets & WebGL Engine Constraints

For real-time delivery in **Three.js** via a single `.glb` container running at 60 FPS on desktop and mobile browsers, the following hard technical constraints are enforced:

### 5.1 Geometry & Polygon Budget
| Level of Detail | Target Triangles | Target Vertices | Purpose |
|-----------------|------------------|-----------------|---------|
| **LOD 0 (Hero)**| 28,000 – 38,000  | 18,000 – 24,000 | Gameplay camera (close to medium range), cinematic intros |
| **LOD 1 (Medium)**| 14,000 – 18,000 | 9,000 – 12,000  | Standard gameplay running camera (5+ meters) |
| **LOD 2 (Far)**   | 6,000 – 8,000   | 3,500 – 5,000   | Distant shadow casting & low-spec fallback |

- **Topology Type:** Clean quad-dominant topology with subdivision-friendly edge loops around primary deformation axes (patella, elbow, shoulder capsule, hip crease).
- **Manifold Integrity:** 100% 2-manifold geometry. Zero non-manifold edges, zero zero-area faces, zero unmerged duplicate vertices, zero stray floating vertices.

### 5.2 Material Groups & Draw Calls
To maintain minimal draw call overhead in WebGL, the character must use **no more than 3 distinct material draw calls**:

1. `M_NYRA_Body` (Opaque, PBR Metallic-Roughness):
   - Covers: Head, neck, torso, arms, legs, fingernails, teeth, mouth interior, eyes.
2. `M_NYRA_Apparel` (Opaque, PBR Metallic-Roughness):
   - Covers: Jacket, sports bra, leggings, tactical belt, pouches, gloves, sneakers.
3. `M_NYRA_Alpha` (Alpha Mask / Blend, PBR Metallic-Roughness):
   - Covers: Hair strands, ponytail cards, fringe tendrils, eyelashes, hoop earrings, pendant necklace.

### 5.3 Texture Resolution & Channel Packing
- **Resolution Cap:** 2048 x 2048 maximum resolution for `Apparel` and `Body`; 2048 x 1024 or 1024 x 1024 for `Hair`.
- **glTF Channel Packing Standard:**
  - **BaseColor:** RGB (sRGB color space).
  - **ORM Map:** Linear color space:
    - Red Channel: Ambient Occlusion (baked contact shadowing)
    - Green Channel: Roughness (0.0 = mirror smooth, 1.0 = matte)
    - Blue Channel: Metallic (0.0 = dielectric, 1.0 = raw metal)
  - **Normal Map:** Tangent-space Normal map (+X, +Y, +Z glTF standard), linear color space.
  - **Alpha / Mask (for Hair/Eyelashes):** Alpha channel in BaseColor texture (`alphaMode: MASK`, `alphaCutoff: 0.5`).
- **Target File Size:**
  - Uncompressed GLB: <= 16 MB.
  - Draco / Meshopt + KTX2 compressed runtime container: **<= 6.5 MB**.

### 5.4 Skeleton & Skinning Conventions
- **Root Orientation:** `root` bone at origin `(0, 0, 0)`, facing `+Z` (or Three.js standard `-Z` forward, `+Y` up).
- **Total Bone Count:** 68 to 78 deform bones:
  - Standard Humanoid Core: 54 bones (Hips, Spine0-3, Neck, Head, Clavicles, Arms, Hands with 3 finger bones each, Thighs, Calves, Feet, Toes).
  - Secondary Dynamic Bones: 14 to 20 bones:
    - Ponytail: 4 bones (`Hair_01` to `Hair_04`)
    - Left/Right Front Tendrils: 2 bones each (optional for wind)
    - Jacket Sleeves/Hem: 4 bones
    - Tactical Belt Pouches: 2 bones
    - Breasts: 2 bones (subtle motion)
- **Skinning Weights:** Maximum 4 bone influences per vertex (`JOINTS_0`, `WEIGHTS_0`). Normalized to $\sum W = 1.0$.

---

## 6. Acceptance Criteria & Phase Gate

Before any candidate foundation is cleared for Phase 2 implementation, it must pass the following binary quality gates:

1. **Facial Identity Gate:** The face must possess the mature, attractive, almond-eyed identity of the approved portrait (`references/turnarounds/nyra_portrait_face.png`). Models with juvenile, cartoon, or hyper-stylized facial features are disqualified.
2. **Abdominal Topology Gate:** The abdominal wall between underbust and waist must be clean, smooth, and anatomically coherent without shelf artifacts or collapsed polygons.
3. **Apparel Completeness Gate:** The outfit must match the off-shoulder cropped jacket, sports bra, high-waisted chevron leggings, and chunky sneaker combination.
4. **License Compliance Gate:** Must possess an unambiguous commercial license that permits serving the 3D asset in a browser-based Three.js WebGL game without violating third-party extraction clauses (see `production_v3/research/LICENSE_RISK_MATRIX.md`).

---
*Signed and locked for Phase 0 completion.*
