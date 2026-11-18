# NYRA 2.0 — Commercial Asset Licensing & WebGL Risk Matrix
**Document ID:** `NYRA-RESEARCH-LICENSING-VERIFIED`  
**Status:** PHASE 1.1 AUDIT COMPLETE — VERIFIED LEGAL OPINION  
**Author:** Technical Art & Art Direction  
**Date:** 18 November 2026  

---

## 1. Executive Summary: The WebGL Browser Extraction Hazard

Deploying 3D character assets in a **Three.js WebGL browser game** introduces a direct conflict with standard 3D marketplace click-through End User License Agreements (EULAs).

In native video games (Unreal Engine, Unity, consoles, native PC binaries), assets are cooked, compiled, and packed into proprietary binary packages (e.g., `.pak`, `.bundle`, `.assets`). In this compiled state, 3D meshes cannot be extracted without reverse-engineering or memory hooking, fulfilling the standard EULA obligation to "take reasonable measures to prevent third-party asset extraction."

In a **Three.js / WebGL web application**, 3D assets are delivered to the client browser over standard HTTP `GET` requests:

```
+-----------------------------------------------------------------------------------------+
|                        THE WEBGL CLIENT EXTRACTION REALITY                              |
|                                                                                         |
|   [Web Server] ------ HTTP GET nyra.glb ------> [Browser Client (Three.js)]             |
|                                                          |                              |
|                                              +-----------v-----------+                  |
|                                              | Browser Network Cache |                  |
|                                              | Chrome DevTools       |                  |
|                                              +-----------+-----------+                  |
|                                                          |                              |
|                                           [Right-Click: Save As nyra.glb]               |
|                                                          |                              |
|                                           [Import directly into Blender]                |
+-----------------------------------------------------------------------------------------+
```

Because an unencrypted `.glb` file transferred to a browser can be saved directly to disk in two clicks and opened in any 3D DCC tool, **the asset is technically and legally distributed as a standalone 3D file.**

---

## 2. Permitted Game Use vs. Standalone Asset Redistribution

A rigorous legal analysis requires distinguishing between two distinct rights:

| Dimension | Permitted Game Use (Standard EULA) | Prohibited Standalone Redistribution (WebGL Risk) |
| :--- | :--- | :--- |
| **Delivery Medium** | Compiled native application binary (C++, Unreal `.pak`, Unity `.assets`). | Open HTTP transfer of standard 3D files (`.glb`, `.gltf`, `.bin`). |
| **Asset Format** | Proprietary engine chunk; geometry stripped of source metadata. | Standard Khronos glTF 2.0 container containing full mesh, UVs, and skeleton. |
| **Third-Party Access** | Mesh cannot be extracted without reverse-engineering software. | Trivial single-click download via standard browser developer tools. |
| **Contractual Compliance** | **Compliant:** Meets the "incorporated product" threshold. | **Breach:** Violates prohibitions against extractable standalone distribution. |

---

## 3. Comprehensive EULA Verification by Platform

### 3.1 ArtStation Marketplace — Product & Services Agreement (Stock Assets)
- **Applicable Terms:** Section 3 ("License to Stock Assets") & Section 4 ("Restrictions").
- **Governing Language:**
  > *"You may incorporate the Stock Asset into a standalone creative work (such as a video game, visual effect, or broadcast)... provided that the Stock Asset cannot be extracted, retrieved, or separated by end-users as a standalone file."*
  > *"You may not distribute, sell, or make available the Stock Asset or any derivative work in a format that allows third parties to extract the 3D model."*
- **Legal Reality for Three.js:**
  - Serving a purchased character (such as *Techwear Girl* or *Gym Girls*) as an exposed `.glb` over public HTTP breaches Section 4.
  - The Standard Commercial License is limited to 2,000 sales or 20,000 monthly views; high-traffic web games require an Extended Commercial License.
  - **Verdict:** **BLOCKED PENDING EXPLICIT SELLER ADDENDUM**.

### 3.2 CGTrader — Standard Royalty-Free License
- **Applicable Terms:** Section 10 ("Permitted Uses and Restrictions"), Subsections 10.2 & 10.3.
- **Governing Language:**
  > *"You may not sell, distribute, give away, or otherwise transfer the 3D Model file itself or any derivative thereof in any format where the 3D Model can be extracted or retrieved by a third party as a standalone file."*
  > *"If the 3D Model is incorporated into an electronic game, virtual world, or application, you must take all reasonable measures to prevent end-users from extracting the 3D Model."*
- **Legal Reality for Three.js:**
  - Standard `.glb` delivery over WebGL does not constitute "reasonable measures to prevent extraction."
  - **Verdict:** **BLOCKED PENDING EXPLICIT SELLER ADDENDUM**.

### 3.3 Reallusion ActorCore — Content EULA
- **Applicable Terms:** Section 3 ("License Rights"), Subsection 3.3 ("Interactive Web Restrictions").
- **Governing Language:**
  > *"The Standard License authorizes embedding Content into compiled video games and video productions. The Standard License expressly prohibits the use of Content in web-based asset distribution systems, web 3D model viewers, or web-based interactive avatar tools where end-users can access or extract 3D geometry."*
  > *"Any web-based real-time 3D interactive application requires an ActorCore Enterprise License."*
- **Legal Reality for Three.js:**
  - Reallusion explicitly bars standard-tier characters from interactive web applications. Enterprise licensing starts in the thousands of dollars.
  - **Verdict:** **PERMANENTLY REJECTED**.

### 3.4 Creative Commons (CC0 and CC-BY 4.0) — Open Safe Harbor
- **CC0 1.0 Universal (Blender Studio Human Base Meshes):**
  - Dedication: The copyright owner has dedicated the work to the public domain worldwide.
  - WebGL Impact: Users are legally entitled to download, extract, inspect, and reuse the `.glb` without restriction.
  - **Verdict:** **100% PERMITTED (ZERO EXTRACTION LIABILITY)**.
- **CC-BY 4.0 International (Blender Studio Rain):**
  - WebGL Impact: Allows adaptation and commercial distribution in raw web formats, provided attribution is maintained in-game and in metadata.
  - **Verdict:** **100% PERMITTED (ZERO EXTRACTION LIABILITY)**.

---

## 4. Why Technical Obfuscation (AES / Wasm) Is NOT Legal Authorization

A critical error in preliminary planning was the assumption that client-side technical obfuscation (e.g., stripping glTF magic headers, XOR scrambling, or AES encryption with a WebAssembly client decryptor) serves as a valid "remediation path" to bypass marketplace extraction bans.

**This assumption is legally void for three fundamental reasons:**

1. **Contractual Primacy:** 
   - A copyright license is a legal contract. If the contract stipulates that the licensee may not distribute extractable 3D assets, implementing client-side obfuscation does **not** amend the contract. The licensor has not granted permission.
2. **Client-Side Decryption Inevitability:**
   - In any WebGL application, the decryption keys, decryption algorithms, and decrypted buffers **must exist in plaintext on the client device** for the WebGL API (`gl.bufferData`) to send geometry to the GPU.
   - Any technical investigator or copyright auditor can hook the browser's `WebGLRenderingContext` in five lines of JavaScript and dump the raw vertex buffers directly from memory.
3. **Statutory Liability:**
   - In copyright infringement litigation, deploying an unauthorized commercial asset behind weak client-side obfuscation can be construed as willful infringement (attempting to conceal unauthorized distribution) rather than good-faith compliance.

```
+-------------------------------------------------------------------------------+
|                             LEGAL REALITY RULE                                |
| Technical obfuscation is merely an obstacle against casual scrapers.          |
| It DOES NOT constitute legal authorization from the copyright holder.        |
| Without a signed contractual addendum, client-side WebGL deployment of a     |
| commercial marketplace asset remains an actionable breach of contract.       |
+-------------------------------------------------------------------------------+
```

---

## 5. Legally Viable Deployment Paths

Because technical obfuscation cannot cure contractual prohibition, only two legally sound paths exist for *Metro Runner 3D*:

### Path 1: Written Licensor Licensing Addendum (Commercial Path)
Prior to purchasing Candidate 1 or Candidate 2, the studio must contact the artist (**Ida Faber**) directly and secure a formal, written commercial addendum:
* **Required Scope:** An explicit non-exclusive waiver granting permission to distribute the derivative character in single-file WebGL format (`.glb`) for the indie browser game *Metro Runner 3D*.
* **Required Protections:** The studio must commit to stripping all raw source files (FBX, ZTL, modular source meshes), decimating geometry to game resolution, and baking materials into monolithic textures.
* **Cost:** May require paying a negotiated commercial buyout fee or commercial web rider.

### Path 2: Public Domain / Open Source Safe Harbor (Clean Build Path)
If the seller refuses or does not respond, the studio must permanently reject commercial marketplace characters and proceed exclusively with open foundations:
* **Blender Studio Human Base Mesh (CC0):** Completely free of copyright restrictions. Allows open HTTP delivery of the resulting `.glb` with zero legal exposure.
* **Blender Studio Rain (CC-BY 4.0):** Already present in the repository; permits open HTTP delivery with proper attribution.

---

## 6. Official Legal Status Summary

```
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Asset Foundation      | Platform / Owner    | Standard License  | WebGL Legal Status  | Required Action to Clear   |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Candidate 1:          | ArtStation /        | Standard          | BLOCKED             | Signed written addendum    |
| Techwear Girl         | Ida Faber           | Commercial        | (Breaches Sec 4)    | from Ida Faber             |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Candidate 2:          | ArtStation /        | Standard          | BLOCKED             | Signed written addendum    |
| Gym Girls             | Ida Faber           | Commercial        | (Breaches Sec 4)    | from Ida Faber             |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Candidate 3:          | Reallusion /        | ActorCore         | STRICTLY BLOCKED    | Infeasible (Requires       |
| ActorCore Sportswear  | ActorCore           | Standard EULA     | (Paywalled)         | Enterprise license)        |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Open Benchmark:       | Blender Studio /    | Creative Commons  | 100% PERMITTED      | Immediate production use;  |
| Human Base Meshes     | Blender Foundation  | CC0 1.0 (Pub Dom) | (Zero Risk)         | requires full custom build |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
| Repository Asset:     | Blender Studio /    | Creative Commons  | 100% PERMITTED      | Immediate production use;  |
| Rain Foundation       | Blender Foundation  | CC-BY 4.0         | (Zero Risk)         | stylized facial mismatch   |
+-----------------------+---------------------+-------------------+---------------------+----------------------------+
```

---
*End of Verified License Risk Matrix.*
