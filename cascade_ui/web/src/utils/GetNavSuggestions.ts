import type { Type, NavSuggestions } from "@/models/Nav";

export default async function GetNavSuggestions(
  query: string,
  limit: number = 50,
  kinds?: Type[]
): Promise<NavSuggestions> {
  const empty: NavSuggestions = { items: [], total: 0 };
  try {
    const response = await fetch("/v1/search/nav/suggestions", {
      method: "post",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, limit: limit, kinds: kinds ?? null })
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
