import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const host=document.querySelector('#comparison'), panels=[];
let syncing=false;
function pose(kind){
  const views={front:[0,.05,3.5],rear:[0,.05,-3.5],side:[-3.5,.05,0],three:[2.1,.35,3.1],face:[.06,.68,.8]};
  panels.forEach(p=>{p.camera.position.fromArray(views[kind]);p.controls.target.set(0,kind==='face'?.68:0,0);p.controls.update();});
}
async function panel(asset){
  const card=document.createElement('article');card.className='comparison-card';
  const title=document.createElement('h3');title.textContent=asset.label;card.append(title);
  const canvas=document.createElement('canvas');canvas.setAttribute('aria-label',`${asset.label} interactive actual mesh`);card.append(canvas);
  const status=document.createElement('p');status.className='comparison-status';status.textContent='Loading actual geometry…';card.append(status);host.append(card);
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;
  const scene=new THREE.Scene();scene.background=new THREE.Color('#23212b');
  scene.add(new THREE.HemisphereLight(0xfff3e7,0x53596d,2));
  for(const [x,y,z,intensity,color] of [[-3,4,4,2,0xffeddf],[3,2,1,1,0xdbe7ff],[2,3,-3,2,0xcbd0ff]]){const light=new THREE.DirectionalLight(color,intensity);light.position.set(x,y,z);scene.add(light);}
  const camera=new THREE.PerspectiveCamera(35,1,.01,30);camera.position.set(0,.05,3.5);
  const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.minDistance=.25;controls.maxDistance=8;
  const p={renderer,scene,camera,controls,model:null};panels.push(p);
  controls.addEventListener('change',()=>{if(syncing)return;syncing=true;for(const other of panels){if(other===p)continue;other.camera.position.copy(camera.position);other.camera.quaternion.copy(camera.quaternion);other.controls.target.copy(controls.target);other.controls.update();}syncing=false;});
  new ResizeObserver(()=>{const w=card.clientWidth;renderer.setSize(w,w*1.45,false);camera.aspect=1/1.45;camera.updateProjectionMatrix();}).observe(card);
  async function load(path,label){
    status.textContent=`Loading ${label}…`;
    try{
      const gltf=await new GLTFLoader().loadAsync(path);
      if(p.model){scene.remove(p.model);p.model.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[])){for(const v of Object.values(m))if(v?.isTexture)v.dispose();m.dispose();}});}
      p.model=gltf.scene;const box=new THREE.Box3().setFromObject(p.model),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());const scale=1.78/size.y;p.model.scale.multiplyScalar(scale);p.model.position.sub(center.multiplyScalar(scale));scene.add(p.model);
      let tris=0;p.model.traverse(o=>{if(o.isMesh){tris+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;for(const m of [].concat(o.material))m.wireframe=document.querySelector('#compare-wire').checked;}});
      status.textContent=`${label} · ${Math.round(tris).toLocaleString()} triangles · static, unapproved`;
      card.dataset.loaded='true';
    }catch(error){status.textContent=`Load failed: ${error.message}`;card.dataset.loaded='false';}
  }
  if(asset.variants){const select=document.createElement('select');select.setAttribute('aria-label',`${asset.label} texture version`);for(const v of asset.variants){const opt=document.createElement('option');opt.value=v.path;opt.textContent=v.label;select.append(opt);}select.onchange=()=>load(select.value,select.selectedOptions[0].textContent);card.insertBefore(select,canvas);await load(select.value,select.selectedOptions[0].textContent);}else {const fixed=document.createElement('select');fixed.disabled=true;fixed.setAttribute('aria-label',`${asset.label} texture version`);const opt=document.createElement('option');opt.textContent='Preserved Phase 2 textures';fixed.append(opt);card.insertBefore(fixed,canvas);await load(asset.path,asset.label);}
}
try{
  const response=await fetch('../recovery/nyra/comparison-assets.json');if(!response.ok)throw new Error('Candidate manifest is not ready');const assets=await response.json();await Promise.all(assets.map(panel));
  document.querySelectorAll('[data-comparison-view]').forEach(b=>b.onclick=()=>pose(b.dataset.comparisonView));
  document.querySelector('#compare-wire').onchange=e=>panels.forEach(p=>p.model?.traverse(o=>{if(o.isMesh)for(const m of [].concat(o.material))m.wireframe=e.target.checked;}));
  function draw(){requestAnimationFrame(draw);for(const p of panels){p.controls.update();p.renderer.render(p.scene,p.camera);}}draw();
}catch(error){host.textContent=error.message;}
