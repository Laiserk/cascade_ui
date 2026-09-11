import type { PlotResponse } from "@/models/Plots";

export default async function GetPlotSeries(
  lines: string[],
  fields: string[]
): Promise<PlotResponse> {
  const empty: PlotResponse = { series: [], plot_fields: [], not_found: [] };
  try {
    const response = await fetch("/v1/plot_line_series", {
      method: "post",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lines: lines, fields: fields })
    });
    if (!response.ok) {
      return empty;
    }
    return await response.json();
  } catch (error) {
    console.log(error);
    return empty;
  }
}
