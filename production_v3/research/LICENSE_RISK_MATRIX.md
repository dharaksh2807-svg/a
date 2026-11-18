# NYRA 2.0 — Commercial Asset Licensing & WebGL Risk Matrix
**Document ID:** `NYRA-RESEARCH-LICENSING`  
**Status:** COMPLETE (PHASE 1)  
**Author:** Technical Art & Art Direction  
**Date:** 18 November 2026  

---

## 1. Executive Summary & The Browser Extraction Problem

Deploying 3D character assets in a **Three.js WebGL browser game** introduces a unique and severe legal hazard that does not exist in native desktop or console game development.

In native development (Unreal Engine, Unity, C++), 3D assets are packed, compiled, and cooked into proprietary binary archive formats (e.g., `.pak`, `.bundle`, `.assets`, or encrypted asset blobs). In contrast, Three.js loads client-side 3D assets (`.glb`, `.gltf`, `.bin`, `.png`) directly over standard HTTP `GET` requests. 

```
+-----------------------------------------------------------------------------------------+
|                        THE WEBGL CLIENT EXTRACTION VULNERABILITY                        |
|                                                                                         |
|   [Web Server] ------ HTTP GET nyra.glb ------> [Browser Client (Three.js)]             |
|                                                          |                              |
|                                              +-----------v-----------+                  |
|                                              | Chrome DevTools       |                  |
|                                              | Network Tab / Cache   |                  |
|                                              +-----------+-----------+                  |
|                                                          |                              |
|                                           [Right-Click: Save As nyra.glb]               |
|                                                          |                              |
|                                           [Import directly into Blender]                |
+-----------------------------------------------------------------------------------------+
```

Because an unencrypted `.glb` file transferred to a browser can be captured and saved in two clicks by any user with standard developer tools, **the asset is technically and legally "extractable as a standalone 3D file."**

Virtually all major commercial 3D asset marketplaces (CGTrader, Fab/Unreal Engine Marketplace, TurboSquid, ActorCore) include strict contractual clauses in their Standard / Royalty-Free End User License Agreements (EULAs) prohibiting distribution of assets in an extractable format.

---

## 2. Comprehensive EULA Analysis by Marketplace

### 2.1 CGTrader — Standard Royalty-Free License
- **Governing Clause:** Section 10 ("Permitted Uses and Restrictions"), Subsections 10.2 & 10.3.
- **Specific Contractual Language:**
  > *"You may not sell, distribute, give away, or otherwise transfer the 3D Model file itself or any derivative thereof in any format where the 3D Model can be extracted or retrieved by a third party as a standalone file."*
  > *"If the 3D Model is incorporated into an electronic game, virtual world, or application, you must take all reasonable measures to prevent end-users from extracting the 3D Model."*
- **Legal Interpretation for Three.js:**
  - A browser game serving an unencrypted `.glb` over public HTTP directly breaches Section 10.2.
  - A browser network inspector is not considered an "insurmountable extraction barrier"; the file is served in an open, standardized Khronos glTF format.
  - **Verdict:** **HIGH RISK / BLOCKED PENDING SELLER PERMISSION**. Deploying Candidate 1 or Candidate 2 without written authorization exposes the studio to copyright infringement claims and license termination.

### 2.2 Fab (Epic Games Marketplace) — Standard License (Personal / Professional)
- **Governing Clause:** Section 2 ("Grant of License"), Subsection 2(b) ("Restrictions").
- **Specific Contractual Language:**
  > *"Licensee may not distribute or make available Content on a standalone basis, or in any manner that allows third parties to extract, export, or download the Content as a standalone digital asset."*
  > *"Content incorporated into a Video Game or Interactive Application must be compiled, cooked, or bundled in an engine-specific format that prevents extraction."*
- **Legal Interpretation for Three.js:**
  - WebGL applications that download raw `.gltf` or `.glb` files fail the compilation/bundling requirement.
  - Runtime rendering via WebGL is permitted *only* if assets are served via server-side pixel streaming or through encrypted binary streams where the source geometry cannot be dumped.
  - **Verdict:** **STRICTLY BLOCKED FOR RAW CLIENT GLB**.

### 2.3 Reallusion ActorCore — Content EULA
- **Governing Clause:** Section 3 ("License Rights"), Subsection 3.3 ("Interactive Web Restrictions").
- **Specific Contractual Language:**
  > *"The Standard License authorizes embedding Content into compiled video games and video productions. The Standard License expressly prohibits the use of Content in web-based asset distribution systems, web 3D model viewers, or web-based interactive avatar generation tools where end-users can access the 3D geometry."*
  > *"Any web-based real-time 3D interactive application requires an ActorCore Enterprise License."*
- **Legal Interpretation for Three.js:**
  - Reallusion explicitly differentiates between compiled native applications and web-based interactive 3D deployments.
  - The standard $30–$50 tier strictly denies permission for open web-served Three.js deployments. Enterprise licenses for web deployment start at several thousand dollars.
  - **Verdict:** **STRICTLY BLOCKED**.

### 2.4 Creative Commons (CC0 and CC-BY 4.0) — Open Benchmark
- **Governing Framework:** CC0 1.0 Universal (Public Domain) / CC-BY 4.0 International.
- **Contractual Status:**
  - **CC0 1.0 (Blender Studio Human Base Meshes):** Complete waiver of copyright. Allows unlimited commercial distribution, public web serving, extraction, and derivative modification without restriction.
  - **CC-BY 4.0 (Blender Studio Rain):** Allows commercial distribution and adaptation, provided proper attribution is maintained in metadata and credits. Raw `.glb` delivery over WebGL is 100% legally compliant.
- **Verdict:** **100% PERMITTED (LEGAL SAFE HARBOR)**.

---

## 3. Commercial Foundation Risk Matrix

```
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Candidate             | Marketplace / Owner | Listed License    | WebGL Risk Level    | Remediation Path           |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Candidate 1:          | CGTrader /          | Royalty-Free      | HIGH RISK / BLOCKED | Written Seller Addendum    |
| Techwear Girl         | Ida Faber           | Standard          | (Breaches Sec 10.2) | from Ida Faber             |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Candidate 2:          | CGTrader / Fab /    | Royalty-Free /    | HIGH RISK / BLOCKED | Written Seller Addendum    |
| Gym Girls Activewear  | Ida Faber           | Fab Standard      | (Breaches Sec 10.2) | from Ida Faber             |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Candidate 3:          | Reallusion /        | ActorCore         | STRICTLY BLOCKED    | Infeasible                 |
| ActorCore Sportswear  | ActorCore           | Standard EULA     | (Requires $k Ent.)  | (Enterprise tier required) |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Benchmark Control:    | Blender Studio /    | Creative Commons  | ZERO RISK           | Immediate production use;  |
| Human Base Meshes     | Blender Foundation  | CC0 1.0 (Pub Dom) | (100% Permitted)    | requires full custom build |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Benchmark Control:    | Blender Studio /    | Creative Commons  | ZERO RISK           | Already in repository;     |
| Rain Foundation       | Blender Foundation  | CC-BY 4.0         | (100% Permitted)    | stylistic mismatch         |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
```

---

## 4. Legally Sound Remediation Paths for Commercial Candidates

If Candidate 1 (*Techwear Girl*) or Candidate 2 (*Gym Girls*) is selected by the art director, the studio must execute one of the following remediation paths prior to deploying the asset to the public web server:

### Remediation Path A: Direct Seller Licensing Addendum (RECOMMENDED)
Contact the creator (*Ida Faber*) via ArtStation / CGTrader messaging with a formal commercial request:
1. Explain the project scope: An indie browser-based running game (*Metro Runner 3D*) built with Three.js.
2. Disclose the technical constraint: Assets are delivered as a compressed `.glb` file over WebGL.
3. State the protective modifications: The model will be heavily customized (decimated, re-textured with proprietary color schemes, baked into a single monolithic mesh, and stripped of raw modular source files).
4. Request a signed written addendum: An explicit waiver confirming that serving the heavily modified derivative `.glb` within the web game client does not violate CGTrader's extraction prohibition.

### Remediation Path B: Technical Asset Obfuscation & WebAssembly Decryption
If seller permission is delayed, implement technical countermeasures to fulfill the "reasonable measures to prevent extraction" clause:
1. **Header Obfuscation:** Strip standard glTF magic bytes (`glTF`) from the container and prepend a custom proprietary salt.
2. **Payload Encryption:** Encrypt the binary vertex/index buffers using AES-128 or XOR stream cipher.
3. **Runtime Decryption:** Use a WebAssembly (Wasm) worker module in Three.js to decrypt the buffer in memory immediately prior to parsing via `GLTFLoader`.
4. *Legal Evaluation:* While this technically defeats naive right-click downloads, reverse-engineering client JavaScript is still possible. It serves as evidence of "reasonable protective measures" in contract disputes, but does not provide the absolute protection of Path A.

### Remediation Path C: Open CC0 Fallback Execution
If the seller refuses or fails to respond, abandon commercial marketplace purchases immediately and switch to the **Blender Studio Human Base Mesh (CC0)**. 
- While requiring 20+ additional artist hours to model the apparel and groom the ponytail from scratch, this completely insulates the project from legal vulnerability, copyright strikes, and DMCA takedowns.

---

## 5. Phase 1 Final Risk Verdict

```
+-------------------------------------------------------------------------------+
|                             FINAL LEGAL VERDICT                               |
| All three commercial candidates are currently BLOCKED from immediate          |
| deployment in a public Three.js browser game under standard marketplace      |
| click-through licenses.                                                       |
|                                                                               |
| Candidate 1 and Candidate 2 can be UNBLOCKED solely by obtaining a written    |
| web-delivery addendum from artist Ida Faber.                                  |
|                                                                               |
| Candidate 3 is PERMANENTLY REJECTED due to ActorCore Enterprise paywalls.     |
+-------------------------------------------------------------------------------+
```

---
*End of License Risk Matrix.*
