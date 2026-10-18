import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer/decoder';
await MeshoptDecoder.ready;
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
function bounds(doc){const result=new Map();for(const n of doc.getRoot().listNodes()){if(!n.getMesh())continue;const m=n.getWorldMatrix(),lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity],v=[];for(const prim of n.getMesh().listPrimitives()){const a=prim.getAttribute('POSITION');for(let i=0;i<a.getCount();i++){a.getElement(i,v);for(let k=0;k<3;k++){const x=m[k]*v[0]+m[k+4]*v[1]+m[k+8]*v[2]+m[k+12];lo[k]=Math.min(lo[k],x);hi[k]=Math.max(hi[k],x)}}}result.set(n.getName(),[...lo,...hi])}return result}
const before=bounds(await io.read('public/models/robo-jack.glb')), after=bounds(await io.read('public/models/robo-jack.meshopt.glb'));let max=0;for(const [name,b]of before){if(!after.has(name))throw Error(`Missing ${name}`);b.forEach((v,i)=>max=Math.max(max,Math.abs(v-after.get(name)[i])))}if(max>0.0001)throw Error(`Bounds changed ${max}m`);console.log({parts:before.size,maxBoundsDeviationMeters:max});
