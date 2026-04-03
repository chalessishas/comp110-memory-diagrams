/**
 * Pre-render LaTeX to SVG data URI in Node.js.
 * Used because Revideo's built-in Latex component crashes in headless mode.
 * mathjax-full is already installed as a dependency of @revideo/2d.
 */
import { mathjax } from "mathjax-full/js/mathjax.js";
import { TeX } from "mathjax-full/js/input/tex.js";
import { SVG } from "mathjax-full/js/output/svg.js";
import { liteAdaptor } from "mathjax-full/js/adaptors/liteAdaptor.js";
import { RegisterHTMLHandler } from "mathjax-full/js/handlers/html.js";
import { AllPackages } from "mathjax-full/js/input/tex/AllPackages.js";

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);

const tex = new TeX({ packages: AllPackages });
const svg = new SVG({ fontCache: "none" }); // inline paths, self-contained SVG
const doc = mathjax.document("", { InputJax: tex, OutputJax: svg });

/**
 * Convert LaTeX string to a base64 SVG data URI.
 * Synchronous, no network calls.
 * @param latex - TeX math string (e.g. "x = \\frac{-b}{2a}")
 * @param color - SVG foreground color (default: #ffe066 yellow on chalkboard)
 */
export function texToSvgDataUri(
  latex: string,
  color = "#ffe066"
): string {
  const node = doc.convert(latex, { display: true });
  const svgHtml = adaptor
    .innerHTML(node)
    .replace(/currentColor/g, color);
  return "data:image/svg+xml;base64," + Buffer.from(svgHtml).toString("base64");
}

/**
 * Pre-render all formulas in a CourseScript, returning a map of "segIdx-actionIdx" → data URI.
 */
export function preRenderFormulas(
  script: import("./types.js").CourseScript
): Map<string, string> {
  const formulaMap = new Map<string, string>();
  for (let i = 0; i < script.segments.length; i++) {
    for (let j = 0; j < script.segments[i].board.length; j++) {
      const action = script.segments[i].board[j];
      if (action.type === "show_formula") {
        const key = `${i}-${j}`;
        formulaMap.set(key, texToSvgDataUri(action.latex));
      }
    }
  }
  return formulaMap;
}
