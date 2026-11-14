import fs from 'node:fs/promises';
import validator from 'gltf-validator';
let failed=false;
for(const name of ['environment-smoke','rain-geometry-study']) {
  const bytes=await fs.readFile(new URL(`../exports/${name}.glb`,import.meta.url));
  const result=await validator.validateBytes(new Uint8Array(bytes),{uri:`${name}.glb`});
  await fs.writeFile(new URL(`../qa/evidence/${name}-validation.json`,import.meta.url),JSON.stringify(result,null,2)+'\n');
  console.log(name,JSON.stringify({errors:result.issues.numErrors,warnings:result.issues.numWarnings,bytes:bytes.length}));
  failed ||= result.issues.numErrors>0;
}
console.log(failed?'VERDICT: FAIL -- invalid GLB':'VERDICT: PASS');
process.exitCode=failed?1:0;
