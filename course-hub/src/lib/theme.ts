const STORAGE_KEY = "coursehub.theme";

export type ThemeId = "spring" | "sea" | "dusk" | "sakura" | "ink";

export interface ThemeMeta {
  id: ThemeId;
  name: string;
  nameEn: string;
  preview: [string, string, string, string, string];
  isDark: boolean;
}

export const THEMES: ThemeMeta[] = [
  {
    id: "spring",
    name: "春晓",
    nameEn: "Spring Dawn",
    preview: ["#F9F1E4", "#F0E6D6", "#8FA882", "#FBDED0", "#D1E5D9"],
    isDark: false,
  },
  {
    id: "sea",
    name: "海雾",
    nameEn: "Sea Mist",
    preview: ["#EEF2F7", "#E1E7EF", "#6B8CAE", "#D4DCE8", "#B8C8D8"],
    isDark: false,
  },
  {
    id: "dusk",
    name: "暮色",
    nameEn: "Dusk",
    preview: ["#1C1917", "#252220", "#D4A574", "#302C28", "#3D3835"],
    isDark: true,
  },
  {
    id: "sakura",
    name: "樱花",
    nameEn: "Sakura",
    preview: ["#FDF5F3", "#F5E8E4", "#B8847E", "#EAD8D4", "#FBDED0"],
    isDark: false,
  },
  {
    id: "ink",
    name: "墨石",
    nameEn: "Ink Stone",
    preview: ["#18191E", "#1F2128", "#8B9DC3", "#282A32", "#2E3040"],
    isDark: true,
  },
];

export function getSavedTheme(): ThemeId {
  if (typeof window === "undefined") return "spring";
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && THEMES.some((t) => t.id === saved)) return saved as ThemeId;
  } catch {}
  return "spring";
}

export function setTheme(id: ThemeId): void {
  document.documentElement.setAttribute("data-theme", id);
  try {
    localStorage.setItem(STORAGE_KEY, id);
  } catch {}
}

export function initTheme(): void {
  const id = getSavedTheme();
  document.documentElement.setAttribute("data-theme", id);
}
