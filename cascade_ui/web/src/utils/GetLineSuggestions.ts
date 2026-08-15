import type { LineSuggestions } from "@/models/Plots";

export default async function GetLineSuggestions(
  query: string,
  limit: number = 50
): Promise<LineSuggestions> {
  const empty: LineSuggestions = { items: [], total: 0 };
  try {
    const response = await fetch("/v1/search/line/suggestions", {
      method: "post",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, limit: limit })
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
