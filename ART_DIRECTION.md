# NYRA — Urban Velocity

Decision date: 15 November 2026, Asia/Kolkata. Target: a visibly adult woman, approximately 24–26, designed for premium stylized third-person running gameplay. Confidence comes from posture, expression and athletic clothes. Maintain believable joints, useful muscle tone and natural chest/hip proportions.

## Three concepts

| Element | A · NYRA / Urban Velocity | B · SORA / Night Circuit | C · ZURI / Solar Stride |
|---|---|---|---|
| Face | Warm medium-brown skin, almond brown eyes, angular brows, softly squared jaw; composed, lightly mischievous expression | Adult East Asian appearance, refined oval face, straight brows, quieter focused expression | Dark warm skin, sculpted cheekbones, broad expressive smile and strong brows |
| Proportions | About 7.25 heads tall, athletic shoulders, strong calves, lean but not extremely thin waist | About 7 heads, compact agile build, relatively straight athletic silhouette | About 7.25 heads, broad athletic shoulders and sturdy legs |
| Hair | Black swept forelock and high segmented ponytail with coral cuffs | Chin-length black bob, tucked behind one ear | Short sculptural crown of twists |
| Outfit | Cropped coral bomber, cream shoulder inserts, high-neck plum top, tapered plum track pants, cream/coral sneakers | Cobalt cropped windbreaker, mint lining, charcoal top, shorts over opaque leggings, black/mint sneakers | Saffron cropped sleeveless vest, ivory high-neck top, petrol joggers, cream/teal sneakers |
| Materials | Matte technical nylon, ribbed knit cuffs, stretch jersey, mesh/rubber shoes, small reflective double dash | Satin nylon, matte compression fabric, restrained reflective mint piping | Matte ripstop, cotton jersey, slightly textured woven trousers |
| Front silhouette | Broad coral shoulder shape, narrow jacket hem, long tapered legs | Short dark bob and cropped blue volume above a slim lower body | Bare athletic arms frame a bright high collar; loose tapered trousers |
| Rear silhouette | Ponytail rhythm, cream shoulder wings and offset double dash, cream lower-leg accents | Rounded bob, mint upper-back chevron, layered shorts | Twist crown, ivory back arc, petrol lower-body volume |
| Animation | Shorten ponytail to upper shoulder blades; rigid cuffs and 3–4 hair bones; jacket waist clear of hips | Easiest hair setup; shorts/leggings need thigh penetration tests | Simple upper garment; retain space at shoulders and knees, simplify individual twists |
| Personality | Resourceful city navigator; bold and self-possessed | Precise night runner; economical motion | Upbeat urban athlete; expansive energy |
| Modeling difficulty | Medium-high: new face, layered bomber, segmented hair, sneakers | Medium: simpler hair, but layered hip garments | Medium-high: twist sculpt and looser pant deformation |

## Visible review and selection

`references/concepts/runner-concepts.png` is a genuine imagegen output containing front and rear interpretations of all three concepts. It was reviewed visually. It is illustrative concept art with 3D-like shading, not orthographic technical reference or geometry evidence. The exact prompt is retained in `generation-prompt.txt`; no external character art was supplied to generation.

NYRA is selected because her cream shoulders, coral jacket and plum legs remain separated in the rear view, and the ponytail adds a recognizable moving silhouette. SORA has the lowest hair cost but a more familiar jacket/leggings outline. ZURI has excellent color blocking and a strong head silhouette; individual twists and loose trousers introduce more surface and deformation work. These are art-direction judgments, not measured gameplay tests.

The generated sheet is not authoritative for construction. NYRA's ponytail is too long for the desired collision envelope; shorten it. Front/rear clothing seams must be reconciled in a proper turnaround. Sneaker tread/panel detail is too fine for gameplay and should be simplified. The little earrings visible in the output were not requested and are excluded from the production design. The other concepts remain alternatives, not additional modeling commitments.

## Selected design specification

- Palette (sRGB intent): coral `#CB6E55`, plum `#352439`, ivory `#EAE1CE`, hair `#17151B`, warm copper accent `#E8A16A`. Skin is established with painted albedo and lighting tests, not a single flat swatch.
- Adult facial redesign: reduce Rain's exaggerated head/eye proportion only after sculpt studies; develop a distinct brow, cheek plane, nose and jaw. Do not merely recolor Rain. Keep the neutral face attractive in perspective and unlit material inspection, then test smile, blink, frown and effort.
- Keep bomber cuffs above the wrists, hem above hip flexion, no loose scarf, bags or dangling ties. Build a clear collar shape without covering the jaw. Hair should remain visible above the shoulders without crossing the entire back motif.
- Leg accents belong on outer calves, away from knee-fold centers. Sneakers need a readable sole wedge, contrasting toe/heel, and a modest ankle opening. No high heels or oversized soles that distort planted contacts.
- Work in meters with feet at the origin; eventual runtime asset is glTF +Y up. Establish facing convention using the viewer before animations are commissioned.

## Visual acceptance for Phase 2

Review front, rear, profile, three-quarter, face close-up and rear gameplay camera at roughly 180-pixel character height. Test neutral daylight and warm/cool metro lighting. Require a recognizably adult face, distinct identity from Rain, clear values in grayscale, coherent front/rear seams and no glove-like fingers or pinched joints. Judge run, jump, slide and hard side lean before polishing small accessories.
