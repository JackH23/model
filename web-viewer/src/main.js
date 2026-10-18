import { models, assetUrl } from './catalog.js';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import '@fontsource/dm-sans/latin-400.css';
import '@fontsource/dm-sans/latin-500.css';
import '@fontsource/dm-sans/latin-600.css';
import '@fontsource/dm-sans/latin-700.css';
import '@fontsource/space-grotesk/latin-400.css';
import '@fontsource/space-grotesk/latin-500.css';
import '@fontsource/space-grotesk/latin-700.css';
import './style.css';

const $ = (id) => document.getElementById(id);
const modelId = new URLSearchParams(location.search).get('model') || models[0]?.id;
const model = models.find(entry => entry.id === modelId);
if (!model) {
  document.body.innerHTML = '<main style="padding:48px"><h1>Model not found</h1><p>This model is not in the collection.</p><a href="./" style="color:#99e6e7">← Back to library</a></main>';
  throw new Error('Unknown model id');
}
document.title = `${model.name} / Assembly Explorer`;
document.querySelector('.brand').lastElementChild.innerHTML = `${model.name.toUpperCase()}<small>ASSEMBLY EXPLORER</small>`;
document.querySelector('.stage-heading .eyebrow').textContent = `${model.name.toUpperCase()} / 001`;
$('loading').querySelector('strong').textContent = `Assembling ${model.name}`;

const viewport = $('viewport');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(36, 1, 0.01, 100);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x000000, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
viewport.append(renderer.domElement);
renderer.domElement.setAttribute('aria-label', `${model.name} interactive 3D assembly. Drag to orbit, scroll to zoom, click a part to select.`);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.07;
controls.minDistance = 0.15;
controls.maxDistance = 10;
controls.autoRotateSpeed = 0.65;
controls.maxPolarAngle = Math.PI * 0.91;
scene.add(new THREE.HemisphereLight(0xdceff7, 0x242c35, 1.4));
const key = new THREE.DirectionalLight(0xffecd4, 2.6);
key.position.set(3, 5, 4);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.left = key.shadow.camera.bottom = -2;
key.shadow.camera.right = key.shadow.camera.top = 2;
key.shadow.camera.near = 0.1;
key.shadow.camera.far = 15;
key.shadow.bias = -0.00015;
key.shadow.normalBias = 0.004;
scene.add(key);
const rim = new THREE.DirectionalLight(0x8ccff0, 2);
rim.position.set(-3, 3, -2);
scene.add(rim);
const fill = new THREE.DirectionalLight(0xffffff, 1.1);
fill.position.set(-2, 2, 3);
scene.add(fill);
const pmrem = new THREE.PMREMGenerator(renderer);
const room = new RoomEnvironment();
const environment = pmrem.fromScene(room, 0.04);
scene.environment = environment.texture;
scene.environmentIntensity = 0.7;
room.dispose();
pmrem.dispose();
const floor = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), new THREE.ShadowMaterial({ opacity: 0.22 }));
floor.rotation.x = -Math.PI / 2;
floor.position.y = -0.001;
floor.receiveShadow = true;
scene.add(floor);
const grid = new THREE.GridHelper(8, 40, 0x3e626d, 0x2c424c);
grid.position.y = -0.002;
grid.material.transparent = true;
grid.material.opacity = 0.22;
scene.add(grid);
const selectionBox = new THREE.Box3Helper(new THREE.Box3(), 0x99e6e7);
selectionBox.material.depthTest = false;
selectionBox.material.transparent = true;
selectionBox.material.opacity = 0.55;
selectionBox.renderOrder = 10;
selectionBox.visible = false;
scene.add(selectionBox);

const state = { records: [], selected: null, isolate: null, explode: 0, loaded: false };
const groups = ['Head', 'Torso', 'Left arm', 'Right arm', 'Pelvis', 'Left leg', 'Right leg', 'Other'];
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const modelBounds = new THREE.Box3();
const rows = new Map();
let cameraTween = null;
let toastTimer;
function toast(message) {
  $('toast').textContent = message;
  $('toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('toast').hidden = true; }, 2600);
}
function readable(name) {
  return name.replace(/^(Attach|Finish|Ref16|Target|RefHead|Ref|Final|Preview|Leg|Arm|Torso|Pelvis|Head)[_ ]/i, '')
    .replace(/([._])([LR])$/, (_, separator, side) => ` · ${side === 'L' ? 'left' : 'right'}`)
    .replaceAll('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
function regionFor(mesh, center) {
  if (mesh.userData.region) return mesh.userData.region;
  if (model.grouping !== 'robot') return 'Assembly';
  if (center.y > 1.34) return 'Head';
  if (Math.abs(center.x) > 0.27 && center.y > 0.6) return center.x > 0 ? 'Left arm' : 'Right arm';
  if (center.y > 0.93) return 'Torso';
  if (center.y > 0.78) return 'Pelvis';
  return center.x > 0 ? 'Left leg' : 'Right leg';
}
function frame(bounds, direction = new THREE.Vector3(1.5, 0.65, 3), instant = false) {
  if (bounds.isEmpty()) return;
  const size = bounds.getSize(new THREE.Vector3());
  const target = bounds.getCenter(new THREE.Vector3());
  const isWholeModel = size.y > 1;
  const isMobile = window.innerWidth <= 800;
  if (isWholeModel) target.y -= size.y * (isMobile ? 0.055 : 0.025);
  const vFov = THREE.MathUtils.degToRad(camera.fov);
  const hFov = 2 * Math.atan(Math.tan(vFov / 2) * camera.aspect);
  const padding = isWholeModel ? (isMobile ? 1.65 : 1.5) : 1.35;
  const distance = Math.max(size.y / (2 * Math.tan(vFov / 2)), size.x / (2 * Math.tan(hFov / 2)), size.z) * padding;
  const position = target.clone().add(direction.clone().normalize().multiplyScalar(Math.max(0.2, distance)));
  if (instant || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    camera.position.copy(position); controls.target.copy(target); controls.update();
  } else {
    cameraTween = { start: performance.now(), from: camera.position.clone(), to: position, fromTarget: controls.target.clone(), toTarget: target };
  }
}
function fitVisible() {
  const box = new THREE.Box3();
  for (const record of state.records) if (record.mesh.visible) box.union(new THREE.Box3().setFromObject(record.mesh));
  frame(box);
}
function updateTransforms() {
  for (const record of state.records) {
    record.mesh.position.copy(record.initialPosition).add(record.offset).addScaledVector(record.explodeDirection, state.explode * 0.3);
  }
  scene.updateMatrixWorld(true);
  updateSelectionBox();
}
function updateVisibility() {
  for (const record of state.records) {
    record.mesh.visible = !record.hidden && (!state.isolate || state.isolate === record.id);
    const row = rows.get(record.id);
    if (row) row.querySelector('input').checked = record.mesh.visible;
  }
  $('isolate').textContent = state.isolate ? 'End isolation' : 'Isolate';
  if (state.selected) $('hide-selected').textContent = state.selected.hidden ? 'Show part' : 'Hide part';
  updateSelectionBox();
}
function updateSelectionBox() {
  selectionBox.visible = Boolean(state.selected?.mesh.visible);
  if (selectionBox.visible) selectionBox.box.setFromObject(state.selected.mesh);
}
function setWireframe(value) {
  for (const record of state.records) for (const material of record.materials) material.wireframe = value;
}
function select(record) {
  if (state.selected) {
    for (let i = 0; i < state.selected.materials.length; i++) {
      const material = state.selected.materials[i];
      material.emissive?.copy(state.selected.originalEmissive[i].color);
      material.emissiveIntensity = state.selected.originalEmissive[i].intensity;
    }
    rows.get(state.selected.id)?.classList.remove('selected');
  }
  state.selected = record;
  if (record && state.isolate) { state.isolate = record.id; record.hidden = false; }
  $('empty-selection').hidden = Boolean(record);
  $('selection').hidden = !record;
  if (!record) { updateSelectionBox(); return; }
  record.materials.forEach((material) => {
    if (material.emissive) { material.emissive.set(0x64e8ee); material.emissiveIntensity = 0.17; }
  });
  const row = rows.get(record.id);
  row?.classList.add('selected');
  if (row) row.closest('details').open = true;
  $('selected-name').textContent = record.label;
  $('selected-source').textContent = record.mesh.userData.sourceName || record.mesh.name;
  $('selected-region').textContent = record.region.toUpperCase();
  $('selected-material').textContent = [...new Set(record.materials.map((m) => m.name.replace(/^Web_/, '').replace(/^PH1_/, '')))].join(', ') || 'Standard';
  $('selected-triangles').textContent = record.triangles.toLocaleString();
  const size = record.mesh.geometry.boundingBox.getSize(new THREE.Vector3());
  $('selected-size').textContent = [size.x, size.y, size.z].map((v) => v.toFixed(3)).join(' × ');
  for (const axis of ['x', 'y', 'z']) $(`move-${axis}`).value = record.offset[axis].toFixed(2);
  updateVisibility();
}
function buildList(query = '') {
  rows.clear();
  $('parts').replaceChildren();
  const filtered = state.records.filter((r) => `${r.label} ${r.mesh.name} ${r.region}`.toLowerCase().includes(query.toLowerCase()));
  if (!filtered.length) {
    const p = document.createElement('p'); p.className = 'no-results'; p.textContent = 'No parts match your search.'; $('parts').append(p); return;
  }
  for (const group of [...new Set([...groups, ...state.records.map(record => record.region)])]) {
    const records = filtered.filter((r) => r.region === group);
    if (!records.length) continue;
    const details = document.createElement('details'); details.className = 'group';
    details.open = Boolean(query) || group === 'Head' || model.grouping !== 'robot' || state.selected?.region === group;
    const summary = document.createElement('summary'); summary.textContent = group;
    const count = document.createElement('span'); count.className = 'group-count'; count.textContent = String(records.length); summary.append(count); details.append(summary);
    for (const record of records) {
      const row = document.createElement('div'); row.className = `part-row${state.selected === record ? ' selected' : ''}`;
      const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.checked = record.mesh.visible;
      checkbox.setAttribute('aria-label', `Show ${record.label}`);
      checkbox.addEventListener('change', () => {
        if (state.isolate) state.isolate = null;
        record.hidden = !checkbox.checked; updateVisibility();
      });
      const button = document.createElement('button'); button.textContent = record.label; button.title = record.mesh.userData.sourceName || record.mesh.name;
      button.dataset.part = record.mesh.name;
      button.addEventListener('click', () => select(record));
      row.append(checkbox, button); details.append(row); rows.set(record.id, row);
    }
    $('parts').append(details);
  }
}
function hitRecord(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(state.records.filter((r) => r.mesh.visible).map((r) => r.mesh), false);
  return hits.length ? state.records.find((r) => r.mesh === hits[0].object) : null;
}
let down = null;
renderer.domElement.addEventListener('pointerdown', (event) => { if (event.button === 0) down = { x: event.clientX, y: event.clientY }; });
renderer.domElement.addEventListener('pointerup', (event) => {
  if (down && Math.hypot(event.clientX - down.x, event.clientY - down.y) < 5) select(hitRecord(event));
  down = null;
});
renderer.domElement.addEventListener('pointercancel', () => { down = null; });
renderer.domElement.addEventListener('pointermove', (event) => {
  if (event.buttons) { $('hover-label').hidden = true; return; }
  const record = hitRecord(event);
  const label = $('hover-label'); label.hidden = !record;
  renderer.domElement.style.cursor = record ? 'pointer' : 'grab';
  if (record) {
    const rect = viewport.getBoundingClientRect(); label.textContent = record.label;
    label.style.left = `${Math.min(event.clientX - rect.left + 14, rect.width - 190)}px`;
    label.style.top = `${event.clientY - rect.top + 14}px`;
  }
});
renderer.domElement.addEventListener('pointerleave', () => { $('hover-label').hidden = true; down = null; });
controls.addEventListener('start', () => { cameraTween = null; });
$('search').addEventListener('input', (event) => buildList(event.target.value));
$('show-all').addEventListener('click', () => { state.isolate = null; state.records.forEach((r) => { r.hidden = false; }); updateVisibility(); });
$('hide-selected').addEventListener('click', () => { if (!state.selected) return; state.selected.hidden = !state.selected.hidden; updateVisibility(); });
$('isolate').addEventListener('click', () => { if (!state.selected) return; state.selected.hidden = false; state.isolate = state.isolate ? null : state.selected.id; updateVisibility(); });
$('focus').addEventListener('click', () => { if (state.selected) { state.selected.hidden = false; updateVisibility(); frame(new THREE.Box3().setFromObject(state.selected.mesh)); } });
$('reset-part').addEventListener('click', () => { if (!state.selected) return; state.selected.offset.set(0, 0, 0); state.selected.hidden = false; updateTransforms(); select(state.selected); });
for (const axis of ['x', 'y', 'z']) $(`move-${axis}`).addEventListener('input', (event) => {
  if (!state.selected) return;
  const value = Number.parseFloat(event.target.value);
  if (!Number.isFinite(value)) return;
  state.selected.offset[axis] = THREE.MathUtils.clamp(value, -2, 2); updateTransforms();
});
$('explode').addEventListener('input', (event) => { state.explode = Number(event.target.value) / 100; $('explode-value').value = `${event.target.value}%`; updateTransforms(); });
$('rotate').addEventListener('change', (event) => { controls.autoRotate = event.target.checked; });
$('wireframe').addEventListener('change', (event) => setWireframe(event.target.checked));
$('grid-toggle').addEventListener('change', (event) => { grid.visible = event.target.checked; });
$('fit-model').addEventListener('click', fitVisible);
document.querySelectorAll('[data-view]').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('[data-view]').forEach((b) => b.classList.toggle('active', b === button));
  const directions = { perspective: new THREE.Vector3(1.5, 0.65, 3), front: new THREE.Vector3(0, 0.12, 3), side: new THREE.Vector3(3, 0.12, 0), back: new THREE.Vector3(0, 0.12, -3) };
  controls.autoRotate = false; $('rotate').checked = false;
  const bounds = new THREE.Box3(); state.records.filter((r) => r.mesh.visible).forEach((r) => bounds.union(new THREE.Box3().setFromObject(r.mesh)));
  frame(bounds, directions[button.dataset.view]);
}));
$('reset-all').addEventListener('click', () => {
  select(null); state.isolate = null; state.explode = 0;
  state.records.forEach((r) => { r.hidden = false; r.offset.set(0, 0, 0); });
  $('explode').value = '0'; $('explode-value').value = '0%'; $('rotate').checked = false; controls.autoRotate = false;
  $('wireframe').checked = false; setWireframe(false); $('grid-toggle').checked = true; grid.visible = true;
  $('search').value = ''; updateTransforms(); updateVisibility(); buildList(); frame(modelBounds);
  document.querySelectorAll('[data-view]').forEach((b) => b.classList.toggle('active', b.dataset.view === 'perspective'));
  toast('Scene restored');
});
$('download-shot').addEventListener('click', () => {
  renderer.render(scene, camera);
  const link = document.createElement('a'); link.download = 'robo-jack-view.png'; link.href = renderer.domElement.toDataURL('image/png'); link.click();
});
window.addEventListener('keydown', (event) => {
  if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
  if (event.key === 'Escape') { state.isolate = null; select(null); updateVisibility(); }
  if (event.key.toLowerCase() === 'f') { if (state.selected) $('focus').click(); else fitVisible(); }
});
let mobileLayout = window.innerWidth <= 800;
function resize() {
  const width = viewport.clientWidth; const height = viewport.clientHeight;
  camera.aspect = width / Math.max(1, height); camera.updateProjectionMatrix(); renderer.setSize(width, height);
  const mobile = window.innerWidth <= 800;
  if (mobile !== mobileLayout && state.loaded) frame(modelBounds, camera.position.clone().sub(controls.target), true);
  mobileLayout = mobile;
}
new ResizeObserver(resize).observe(viewport);
resize();
renderer.domElement.addEventListener('webglcontextlost', (event) => { event.preventDefault(); toast('Graphics paused. Waiting for the browser to restore WebGL…'); });
renderer.domElement.addEventListener('webglcontextrestored', () => toast('Graphics restored'));
const loader = new GLTFLoader();
loader.load(assetUrl(model.file), (gltf) => {
  const robot = gltf.scene; robot.name = model.name; scene.add(robot); robot.updateMatrixWorld(true);
  robot.traverse((mesh) => {
    if (!mesh.isMesh) return;
    mesh.name = mesh.userData.sourceName || mesh.name;
    mesh.geometry.computeBoundingBox(); mesh.geometry.computeBoundingSphere();
    mesh.castShadow = mesh.geometry.boundingBox.getSize(new THREE.Vector3()).length() > 0.045;
    mesh.receiveShadow = true;
    const originals = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    const materials = originals.map((m) => m.clone()); mesh.material = Array.isArray(mesh.material) ? materials : materials[0];
    const center = new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3());
    const region = regionFor(mesh, center);
    const direction = new THREE.Vector3();
    if (region === 'Head') direction.set(center.x * 0.6, 1.1, center.z * 0.4);
    else if (region.includes('arm')) direction.set(region === 'Left arm' ? 1 : -1, 0.1, center.z * 0.5);
    else if (region.includes('leg')) direction.set(region === 'Left leg' ? 0.65 : -0.65, -0.6, center.z * 0.4);
    else if (region === 'Pelvis') direction.set(Math.sign(center.x) * 0.3, -0.25, center.z >= 0 ? 0.7 : -0.7);
    else direction.set(Math.sign(center.x) * 0.15, 0, center.z >= 0 ? 0.85 : -0.85);
    const record = { id: mesh.uuid, mesh, region, label: mesh.userData.label || readable(mesh.userData.sourceName || mesh.name), materials, originalEmissive: materials.map((m) => ({ color: m.emissive?.clone() || new THREE.Color(), intensity: m.emissiveIntensity ?? 1 })), initialPosition: mesh.position.clone(), offset: new THREE.Vector3(), explodeDirection: direction, hidden: false, triangles: (mesh.geometry.index?.count ?? mesh.geometry.attributes.position.count) / 3 };
    state.records.push(record);
  });
  state.records.sort((a, b) => a.label.localeCompare(b.label));
  modelBounds.setFromObject(robot); buildList(); frame(modelBounds, new THREE.Vector3(1.5, 0.65, 3), true);
  $('part-count').textContent = String(state.records.length); $('load-state').textContent = `${state.records.length} PARTS / READY`;
  $('loading').hidden = true; state.loaded = true;
}, (event) => { $('progress').textContent = event.total ? `${Math.round(event.loaded / event.total * 100)}% · Loading assembly` : `${(event.loaded / 1048576).toFixed(1)} MB loaded`; }, (error) => {
  console.error('Model loading failed', error); $('loading').querySelector('strong').textContent = 'Model could not load';
  $('progress').textContent = `Unable to load ${model.name}. Return to the library or refresh to retry.`; $('load-state').textContent = 'MODEL UNAVAILABLE';
});
renderer.setAnimationLoop((time) => {
  if (cameraTween) {
    const t = Math.min(1, (time - cameraTween.start) / 450); const ease = 1 - (1 - t) ** 3;
    camera.position.lerpVectors(cameraTween.from, cameraTween.to, ease); controls.target.lerpVectors(cameraTween.fromTarget, cameraTween.toTarget, ease);
    if (t === 1) cameraTween = null;
  }
  controls.update(); renderer.render(scene, camera);
});
// Read-only diagnostics for browser verification and future integrations.
window.roboJack = {
  get ready() { return state.loaded; },
  get parts() { return state.records.map((r) => ({ name: r.mesh.name, region: r.region, visible: r.mesh.visible, offset: r.offset.toArray(), position: r.mesh.position.toArray() })); },
  get selected() { return state.selected?.mesh.name || null; },
  get metrics() { return { triangles: renderer.info.render.triangles, drawCalls: renderer.info.render.calls, partCount: state.records.length }; },
  screenPoint(name) {
    const r = state.records.find((item) => item.mesh.name === name); if (!r) return null;
    const point = new THREE.Box3().setFromObject(r.mesh).getCenter(new THREE.Vector3()).project(camera); const rect = renderer.domElement.getBoundingClientRect();
    return { x: rect.left + (point.x + 1) / 2 * rect.width, y: rect.top + (1 - point.y) / 2 * rect.height };
  },
};
