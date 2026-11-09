import { NodeIO } from '@gltf-transform/core';
import { EXTMeshoptCompression, ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { reorder, weld, dedup, prune, quantize } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises';

await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder,
});
const source = '.asset-cache/villages';
const output = 'public/models/villages';
await mkdir(output, { recursive: true });
const manifest = JSON.parse(await readFile(`${source}/manifest.json`, 'utf8'));
const snapshot = doc => doc.getRoot().listNodes().filter(n => n.getMesh()).map(n => ({
  name: n.getName(), extras: n.getExtras(),
}));
function bounds(doc) {
  const result = new Map();
  for (const node of doc.getRoot().listNodes()) {
    if (!node.getMesh()) continue;
    const matrix = node.getWorldMatrix(), low = [Infinity, Infinity, Infinity], high = [-Infinity, -Infinity, -Infinity], vertex = [];
    for (const primitive of node.getMesh().listPrimitives()) {
      const positions = primitive.getAttribute('POSITION');
      for (let i = 0; i < positions.getCount(); i++) {
        positions.getElement(i, vertex);
        for (let axis = 0; axis < 3; axis++) {
          const value = matrix[axis] * vertex[0] + matrix[axis + 4] * vertex[1] + matrix[axis + 8] * vertex[2] + matrix[axis + 12];
          low[axis] = Math.min(low[axis], value); high[axis] = Math.max(high[axis], value);
        }
      }
    }
    result.set(node.getName(), [...low, ...high]);
  }
  return result;
}
for (const entry of manifest) {
  const largeScene = ['crystalbrook-village', 'ashwick-walled-village'].includes(entry.id);
  const file = `${entry.id}.${largeScene ? 'meshopt-v2' : 'meshopt'}.glb`;
  const document = await io.read(`${source}/${entry.id}.glb`);
  const before = snapshot(document);
  const originalBounds = bounds(document);
  if (largeScene) {
    await document.transform(weld(), dedup({ propertyTypes: ['Accessor', 'Material', 'Mesh'] }),
      prune({ keepLeaves: true }),
      quantize({ quantizePosition: 14, quantizeNormal: 10, quantizeTexcoord: 16, cleanup: false }),
      weld(), dedup({ propertyTypes: ['Accessor', 'Material', 'Mesh'] }),
      reorder({ encoder: MeshoptEncoder, target: 'size' }), prune({ keepLeaves: true }));
  } else {
    await document.transform(weld(), dedup({ propertyTypes: ['Accessor', 'Material', 'Mesh'] }),
      prune({ keepLeaves: true }), reorder({ encoder: MeshoptEncoder, target: 'size' }),
      quantize({ quantizePosition: 16, quantizeNormal: 12, quantizeTexcoord: 16, cleanup: false }),
      prune({ keepLeaves: true }));
  }
  // Preserve source parts and topology; bound the quantization error below.
  document.createExtension(EXTMeshoptCompression).setRequired(true)
    .setEncoderOptions({ method: largeScene ? EXTMeshoptCompression.EncoderMethod.FILTER : EXTMeshoptCompression.EncoderMethod.QUANTIZE });
  await io.write(`${output}/${file}`, document);
  const decoded = await io.read(`${output}/${file}`);
  const after = snapshot(decoded);
  if (JSON.stringify(before) !== JSON.stringify(after)) throw Error(`Part metadata changed: ${entry.id}`);
  entry.maxBoundsDeviationMeters = 0;
  for (const [name, box] of bounds(decoded)) {
    box.forEach((value, index) => {
      entry.maxBoundsDeviationMeters = Math.max(entry.maxBoundsDeviationMeters, Math.abs(value - originalBounds.get(name)[index]));
    });
  }
  if (entry.maxBoundsDeviationMeters > 0.001) throw Error(`Bounds changed by more than 1 mm: ${entry.id}`);
  entry.file = file;
  entry.optimizedBytes = (await stat(`${output}/${file}`)).size;
  console.log(`${entry.id}: ${entry.partCount} parts, ${(entry.optimizedBytes / 1048576).toFixed(2)} MB`);
}
await writeFile(`${output}/manifest.json`, JSON.stringify(manifest, null, 2) + '\n');
