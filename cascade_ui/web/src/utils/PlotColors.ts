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
