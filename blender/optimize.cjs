// Shrink the raw Blender exports for the web: merge parts that share a material, weld, quantize, meshopt-compress.
//   npm run models            (reads blender/export/<world>/, writes models/<world>/)
const { execFileSync } = require('child_process'), fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..'), bin = path.join(root, 'node_modules/.bin/gltf-transform');
for (const world of fs.readdirSync(path.join(root, 'blender/export'))) {
  const from = path.join(root, 'blender/export', world), to = path.join(root, 'models', world);
  fs.mkdirSync(to, { recursive: true });
  let before = 0, after = 0;
  for (const f of fs.readdirSync(from)) {
    if (f.endsWith('.json')) { fs.copyFileSync(path.join(from, f), path.join(to, f)); continue; }
    if (!f.endsWith('.glb')) continue;
    if (f === 'seatrain.glb') {        // the textured Sketchfab train: smaller textures as WebP, lighter mesh
      const tmp = path.join(to, '_resized.glb');
      execFileSync(bin, ['resize', path.join(from, f), tmp, '--width', '1024', '--height', '1024'], { stdio: 'ignore' });
      execFileSync(bin, ['optimize', tmp, path.join(to, f), '--compress', 'meshopt', '--texture-compress', 'webp', '--simplify', 'true', '--simplify-ratio', '0.5', '--simplify-error', '0.0005'], { stdio: 'ignore' });
      fs.unlinkSync(tmp);
    } else
    execFileSync(bin, ['optimize', path.join(from, f), path.join(to, f), '--compress', 'meshopt', '--texture-compress', 'false', '--simplify', 'false', '--palette', 'false'], { stdio: 'ignore' });
    before += fs.statSync(path.join(from, f)).size; after += fs.statSync(path.join(to, f)).size;
  }
  console.log(`${world}: ${(before / 1e6).toFixed(1)} MB -> ${(after / 1e6).toFixed(1)} MB`);
}
