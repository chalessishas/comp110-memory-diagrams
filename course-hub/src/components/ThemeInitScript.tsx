/**
 * Inline blocking script to prevent theme flash (FOUC).
 * Reads saved theme from localStorage and applies data-theme
 * BEFORE React hydrates. Must be placed in <head>.
 */
export function ThemeInitScript() {
  const script = `
(function(){
  try {
    var t = localStorage.getItem("coursehub.theme");
    if (t && ["spring","sea","dusk","sakura","ink"].indexOf(t) !== -1) {
      document.documentElement.setAttribute("data-theme", t);
    }
  } catch(e) {}
})();
`;
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}
