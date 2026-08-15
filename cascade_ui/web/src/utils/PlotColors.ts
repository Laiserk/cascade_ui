export const SERIES_COLORS = [
  "#FA003F",
  "#177E89",
  "#DEB841",
  "#4C243B",
  "#8B5FBF",
  "#EE6123",
  "#003091",
  "#00F7FF",
  "#000000",
];

export function seriesColor(index: number): string {
  return SERIES_COLORS[index % SERIES_COLORS.length];
}
