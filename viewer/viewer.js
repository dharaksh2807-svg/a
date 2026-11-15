import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const $=id=>document.getElementById(id);
const stage=$('stage'),status=$('status');
try {
  const renderer=new THREE.WebGLRenderer({canvas:stage.querySelector('canvas'),antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.35;
  const scene=new THREE.Scene();scene.background=new THREE.Color('#29232c');
  const camera=new THREE.PerspectiveCamera(35,1,.01,100);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
  scene.add(new THREE.HemisphereLight(0xfff0df,0x888299,2.2));
  const key=new THREE.DirectionalLight(0xffffff,2.1);key.position.set(3,5,4);scene.add(key);
  const rim=new THREE.DirectionalLight(0xb4c7ff,1.2);rim.position.set(-3,3,-3);scene.add(rim);
  const loader=new GLTFLoader();let model,mixer,action,radius=2,serial=0,last=performance.now();
  let frontPositive=true;
  function viewpoint(rear=false){camera.position.set(0,radius*.18,(rear?-1:1)*(frontPositive?1:-1)*radius*3.25);controls.target.set(0,0,0);controls.update();}
  function release(root){const materials=new Set(),textures=new Set();root.traverse(o=>{o.geometry?.dispose();if(o.material)for(const m of [].concat(o.material)){materials.add(m);for(const value of Object.values(m))if(value?.isTexture)textures.add(value);}});textures.forEach(t=>t.dispose());materials.forEach(m=>m.dispose());}
  function wireframe(){model?.traverse(o=>{if(o.isMesh)for(const m of [].concat(o.material))m.wireframe=$('wire').checked;});}
  function install(gltf,label,request){
    if(request!==serial){release(gltf.scene);return;}
    if(model){scene.remove(model);release(model);}mixer?.stopAllAction();action=null;
    model=gltf.scene;scene.add(model);
    const box=new THREE.Box3().setFromObject(model),size=box.getSize(new THREE.Vector3());
    model.position.sub(box.getCenter(new THREE.Vector3()));radius=Math.max(size.length()/2,.1);
    camera.near=radius/100;camera.far=radius*100;camera.updateProjectionMatrix();viewpoint();
    let triangles=0,meshes=0,skins=0;const materials=new Set();
    model.traverse(o=>{if(o.isMesh){meshes++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;[].concat(o.material).forEach(m=>materials.add(m));}if(o.isSkinnedMesh)skins++;});
    mixer=new THREE.AnimationMixer(model);$('clips').replaceChildren();
    const none=document.createElement('option');none.value='';none.textContent='Rest pose';$('clips').append(none);
    gltf.animations.forEach((clip,i)=>{const option=document.createElement('option');option.value=i;option.textContent=clip.name||`Clip ${i+1}`;$('clips').append(option);});
    $('clips').disabled=!gltf.animations.length;
    $('clips').onchange=()=>{action?.stop();action=null;if($('clips').value!==''){action=mixer.clipAction(gltf.animations[Number($('clips').value)]);action.reset().play();}};
    wireframe();status.textContent=`${label} · ${meshes} meshes · ${Math.round(triangles).toLocaleString()} triangles · ${materials.size} materials · ${skins} skinned meshes · ${gltf.animations.length} clips`;
  }
  async function load(url,label){const request=++serial;status.textContent=`Loading ${label}…`;try{install(await loader.loadAsync(url),label,request);}catch(error){if(request===serial)status.textContent=`Could not load GLB: ${error.message}`;}}
  function bundled(){const name=$('asset').value;frontPositive=name!=='environment-smoke';const notes={'nyra-visual':'NYRA’s actual geometry with baked color textures. Static review model; final rig and gameplay optimization are pending. Blender subsurface scattering and fine bump shading are simplified in this GLB.','rain-geometry-study':'Phase 1 archive: original Rain geometry in clay, not NYRA.','environment-smoke':'Environment test cube only.'};$('asset-note').textContent=notes[name];load(`../exports/${name}.glb`,name);}
  $('asset').onchange=bundled;
  $('file').onchange=async()=>{const file=$('file').files[0];if(!file)return;frontPositive=true;$('asset-note').textContent='Local GLB preview. Files stay on this computer. Compressed Draco/KTX2 assets require additional decoders and are not supported by this Phase 1 bench.';const request=++serial;status.textContent=`Loading ${file.name}…`;try{install(await loader.parseAsync(await file.arrayBuffer(),''),file.name,request);}catch(error){if(request===serial)status.textContent=`Could not load GLB: ${error.message}`;}};
  $('wire').onchange=wireframe;$('front').onclick=()=>viewpoint();$('rear').onclick=()=>viewpoint(true);
  new ResizeObserver(()=>{renderer.setSize(stage.clientWidth,stage.clientHeight,false);camera.aspect=stage.clientWidth/stage.clientHeight;camera.updateProjectionMatrix();}).observe(stage);
  renderer.setAnimationLoop(now=>{const dt=Math.min((now-last)/1000,.05);last=now;mixer?.update(dt);controls.autoRotate=$('spin').checked;controls.update(dt);renderer.render(scene,camera);});
  bundled();
}catch(error){status.textContent=`Viewer unavailable: ${error.message}. Use the Blender renders above.`;}
