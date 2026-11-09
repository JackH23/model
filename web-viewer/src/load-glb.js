// Fetch separately from GLTFLoader so download completion means stream EOF.
// HTTP Content-Length may be the gzip size, while Fetch yields decoded bytes.
// The GLB header contains the correct total for those decoded bytes.
export async function downloadGlb(url, onProgress) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Model download failed: HTTP ${response.status}`);
  if (!response.body) return response.arrayBuffer();
  const reader = response.body.getReader();
  const chunks = [];
  const header = new Uint8Array(12);
  let headerBytes = 0, loaded = 0, total = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    loaded += value.byteLength;
    if (headerBytes < header.length) {
      const count = Math.min(header.length - headerBytes, value.length);
      header.set(value.subarray(0, count), headerBytes);
      headerBytes += count;
      if (headerBytes === header.length) {
        const view = new DataView(header.buffer);
        if (view.getUint32(0, true) === 0x46546c67) total = view.getUint32(8, true);
      }
    }
    onProgress({ loaded, total });
  }
  if (total && total !== loaded) throw new Error('The model download is incomplete');
  const bytes = new Uint8Array(loaded);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  return bytes.buffer;
}
