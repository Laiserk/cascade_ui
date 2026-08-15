export const SERIES_COLORS = [
  "#FA003F",
  "#177E89",
  "#DEB841",
  "#4C243B",
  "#8B5FBF",
  "#EE6123",
  "#003091",
  "#A3A3A3",
  "#00BB19",
];

export function seriesColor(index: number): string {
  return SERIES_COLORS[index % SERIES_COLORS.length];
}

const SHADE_STEP = 16;
const SHADE_MIN = 20;
const SHADE_MAX = 85;
const LIGHT_BASE = 55;

export function hexToHsl(hex: string): [number, number, number] {
  const value = hex.replace("#", "");
  const r = parseInt(value.slice(0, 2), 16) / 255;
  const g = parseInt(value.slice(2, 4), 16) / 255;
  const b = parseInt(value.slice(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const delta = max - min;
  const l = (max + min) / 2;

  let h = 0;
  if (delta !== 0) {
    if (max === r) h = ((g - b) / delta) % 6;
    else if (max === g) h = (b - r) / delta + 2;
    else h = (r - g) / delta + 4;
  }
  h = h * 60;
  if (h < 0) h += 360;

  const s = delta === 0 ? 0 : delta / (1 - Math.abs(2 * l - 1));
  return [h, s * 100, l * 100];
}

export function hslToHex(h: number, s: number, l: number): string {
  const sat = s / 100;
  const light = l / 100;
  const c = (1 - Math.abs(2 * light - 1)) * sat;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = light - c / 2;

  let rgb: [number, number, number];
  if (h < 60) rgb = [c, x, 0];
  else if (h < 120) rgb = [x, c, 0];
  else if (h < 180) rgb = [0, c, x];
  else if (h < 240) rgb = [0, x, c];
  else if (h < 300) rgb = [x, 0, c];
  else rgb = [c, 0, x];

  const part = (value: number) =>
    Math.round((value + m) * 255).toString(16).padStart(2, "0");
  return `#${part(rgb[0])}${part(rgb[1])}${part(rgb[2])}`;
}

export function metricShade(
  base: string,
  metricIndex: number,
  metricCount: number
): string {
  if (metricIndex <= 0 || metricCount <= 1) return base;

  const [h, s, l] = hexToHsl(base);
  const direction = l > LIGHT_BASE ? -1 : 1;
  const shifted = l + direction * SHADE_STEP * metricIndex;

  return hslToHex(h, s, Math.min(SHADE_MAX, Math.max(SHADE_MIN, shifted)));
}
