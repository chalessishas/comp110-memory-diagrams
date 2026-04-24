// Generates public/og.png (1200x630) — the OpenGraph preview image used
// when the live URL is shared in email, Slack, Discord, etc.
//
// Layout mimics the real three-column app (Stack / Heap / Output) so the
// preview actually telegraphs what the tool looks like.
//
// Regenerate after editing the SVG below:
//   npm run og

import { Resvg } from '@resvg/resvg-js'
import { writeFileSync } from 'node:fs'

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#f7fafc"/>

  <rect y="0" width="1200" height="130" fill="#1e7084"/>
  <text x="60" y="72" font-family="Helvetica, Arial, sans-serif" font-size="48" font-weight="700" fill="#ffffff">COMP110 Memory Diagrams</text>
  <text x="60" y="108" font-family="Helvetica, Arial, sans-serif" font-size="20" fill="#cbd5e0">Interactive Python memory visualizer  ·  v0 ruleset</text>

  <!-- Stack column -->
  <rect x="60" y="170" width="340" height="390" fill="#ffffff" stroke="#cbd5e0" stroke-width="2" rx="8"/>
  <rect x="60" y="170" width="340" height="40" fill="#1e7084" rx="8"/>
  <rect x="60" y="200" width="340" height="10" fill="#1e7084"/>
  <text x="78" y="196" font-family="Helvetica, Arial, sans-serif" font-size="18" font-weight="600" fill="#ffffff">Stack</text>

  <rect x="80" y="228" width="300" height="72" fill="#edf2f7" stroke="#1a202c" stroke-width="1.5" rx="4"/>
  <text x="96" y="252" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="#1a202c">Globals</text>
  <line x1="96" y1="262" x2="364" y2="262" stroke="#a0aec0" stroke-dasharray="2,3"/>
  <text x="96" y="284" font-family="Menlo, Consolas, monospace" font-size="13" fill="#2b6cb0">x</text>
  <text x="116" y="284" font-family="Menlo, Consolas, monospace" font-size="13" fill="#a0aec0">=</text>
  <text x="132" y="284" font-family="Menlo, Consolas, monospace" font-size="13" fill="#1a202c">7</text>

  <rect x="80" y="316" width="300" height="130" fill="#fffbea" stroke="#d69e2e" stroke-width="2" rx="4"/>
  <text x="96" y="340" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="#1a202c">double</text>
  <line x1="96" y1="350" x2="364" y2="350" stroke="#a0aec0" stroke-dasharray="2,3"/>
  <text x="96" y="374" font-family="Menlo, Consolas, monospace" font-size="12" fill="#4a5568">RA: 10</text>
  <text x="96" y="394" font-family="Menlo, Consolas, monospace" font-size="12" font-weight="600" fill="#2c7a7b">RV: 14</text>
  <text x="215" y="374" font-family="Menlo, Consolas, monospace" font-size="13" fill="#2b6cb0">n</text>
  <text x="235" y="374" font-family="Menlo, Consolas, monospace" font-size="13" fill="#a0aec0">=</text>
  <text x="251" y="374" font-family="Menlo, Consolas, monospace" font-size="13" fill="#1a202c">7</text>

  <!-- Heap column -->
  <rect x="430" y="170" width="340" height="390" fill="#ffffff" stroke="#cbd5e0" stroke-width="2" rx="8"/>
  <rect x="430" y="170" width="340" height="40" fill="#1e7084" rx="8"/>
  <rect x="430" y="200" width="340" height="10" fill="#1e7084"/>
  <text x="448" y="196" font-family="Helvetica, Arial, sans-serif" font-size="18" font-weight="600" fill="#ffffff">Heap</text>

  <rect x="450" y="228" width="300" height="52" fill="#f0fff4" stroke="#2d3748" stroke-width="1.5" rx="4"/>
  <text x="466" y="258" font-family="Menlo, Consolas, monospace" font-size="14" font-weight="700" fill="#22543d">ID:0</text>
  <text x="518" y="258" font-family="Menlo, Consolas, monospace" font-size="14" fill="#2d3748">fn 1–3</text>
  <text x="596" y="258" font-family="Menlo, Consolas, monospace" font-size="14" font-style="italic" fill="#4a5568">greet</text>

  <rect x="450" y="296" width="300" height="116" fill="#faf5ff" stroke="#6b46c1" stroke-width="1.5" rx="4"/>
  <text x="466" y="322" font-family="Menlo, Consolas, monospace" font-size="14" font-weight="700" fill="#22543d">ID:1</text>
  <text x="518" y="322" font-family="Menlo, Consolas, monospace" font-size="14" fill="#2d3748">list[int]</text>
  <line x1="466" y1="334" x2="734" y2="334" stroke="#a0aec0" stroke-dasharray="2,3"/>
  <text x="466" y="358" font-family="Menlo, Consolas, monospace" font-size="13" fill="#553c9a">[0]</text>
  <text x="500" y="358" font-family="Menlo, Consolas, monospace" font-size="13" fill="#a0aec0">=</text>
  <text x="516" y="358" font-family="Menlo, Consolas, monospace" font-size="13" fill="#1a202c">3</text>
  <text x="466" y="382" font-family="Menlo, Consolas, monospace" font-size="13" fill="#553c9a">[1]</text>
  <text x="500" y="382" font-family="Menlo, Consolas, monospace" font-size="13" fill="#a0aec0">=</text>
  <text x="516" y="382" font-family="Menlo, Consolas, monospace" font-size="13" fill="#1a202c">7</text>
  <text x="466" y="406" font-family="Menlo, Consolas, monospace" font-size="13" fill="#553c9a">[2]</text>
  <text x="500" y="406" font-family="Menlo, Consolas, monospace" font-size="13" fill="#a0aec0">=</text>
  <text x="516" y="406" font-family="Menlo, Consolas, monospace" font-size="13" fill="#1a202c">14</text>

  <!-- Output column -->
  <rect x="800" y="170" width="340" height="390" fill="#ffffff" stroke="#cbd5e0" stroke-width="2" rx="8"/>
  <rect x="800" y="170" width="340" height="40" fill="#1e7084" rx="8"/>
  <rect x="800" y="200" width="340" height="10" fill="#1e7084"/>
  <text x="818" y="196" font-family="Helvetica, Arial, sans-serif" font-size="18" font-weight="600" fill="#ffffff">Output</text>

  <rect x="820" y="228" width="300" height="36" fill="#000000" rx="3"/>
  <text x="834" y="251" font-family="Menlo, Consolas, monospace" font-size="14" fill="#ffe799">Hello, World!</text>

  <rect x="820" y="272" width="300" height="36" fill="#000000" rx="3"/>
  <text x="834" y="295" font-family="Menlo, Consolas, monospace" font-size="14" fill="#ffe799">14</text>

  <text x="60" y="598" font-family="Helvetica, Arial, sans-serif" font-size="17" fill="#4a5568">comp110-mem-diag.vercel.app</text>
  <text x="60" y="618" font-family="Helvetica, Arial, sans-serif" font-size="14" fill="#718096">Step through Stack, Heap, and Output following the COMP110 v0 ruleset.</text>
</svg>`

const resvg = new Resvg(svg, {
  fitTo: { mode: 'width', value: 1200 },
  background: '#f7fafc',
  font: { loadSystemFonts: true },
})
const pngData = resvg.render().asPng()
writeFileSync('public/og.png', pngData)
console.log(`Wrote public/og.png (${pngData.length} bytes, 1200x630)`)
