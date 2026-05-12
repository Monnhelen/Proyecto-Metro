/**
 * Compress images used by intro.html to WebP.
 * Run: node compress_images.js
 * Output files replace originals; originals backed up with .orig extension.
 */
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const BASE = __dirname;

// Images actually referenced in intro.html + hero CSS
const IMAGES = [
  // [input, output, maxWidth, quality]
  ['Foto/fotocrema.jpg',      'Foto/fotocrema.webp',      1920, 82],
  ['Foto/IMG_4780-chica.jpg', 'Foto/IMG_4780-chica.webp', 1200, 80],
  ['Foto/imglargaaaa.jpg',    'Foto/imglargaaaa.webp',    1920, 80],
];

async function compress() {
  for (const [src, dst, maxW, q] of IMAGES) {
    const srcPath = path.join(BASE, src);
    const dstPath = path.join(BASE, dst);
    if (!fs.existsSync(srcPath)) { console.log(`SKIP (not found): ${src}`); continue; }
    const { size: before } = fs.statSync(srcPath);
    await sharp(srcPath)
      .resize({ width: maxW, withoutEnlargement: true })
      .webp({ quality: q })
      .toFile(dstPath);
    const { size: after } = fs.statSync(dstPath);
    const pct = Math.round(100 * (1 - after / before));
    console.log(`${src.padEnd(28)} ${(before/1e6).toFixed(1)}MB -> ${(after/1e6).toFixed(1)}MB  (-${pct}%)`);
    console.log(`  -> ${dst}`);
  }
  console.log('\nDone. Update intro.html to reference the .webp files.');
}

compress().catch(console.error);
