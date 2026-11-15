import fs from 'node:fs/promises';
import validator from 'gltf-validator';
const results=[];
for(const candidate of ['a','b'])for(const suffix of ['', '-pixel-match']){
  const path=`recovery/nyra/candidates/candidate-${candidate}/nyra-${candidate}${suffix}.glb`;
  const bytes=await fs.readFile(path);
  const result=await validator.validateBytes(new Uint8Array(bytes),{uri:path});
  await fs.writeFile(`recovery/nyra/qa/${candidate}${suffix}-gltf-validation.json`,JSON.stringify(result,null,2));
  results.push({path,bytes:bytes.length,errors:result.issues.numErrors,warnings:result.issues.numWarnings});
}
await fs.writeFile('recovery/nyra/qa/glb-validation-summary.json',JSON.stringify(results,null,2));
console.log(JSON.stringify(results));
const failed=results.some(r=>r.errors);console.log(failed?'VERDICT: FAIL -- invalid replacement GLB':'VERDICT: PASS');process.exitCode=failed?1:0;
