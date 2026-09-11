import type { ItemSuggestions } from "@/models/Compare";

export default async function GetItemSuggestions(
  query: string,
  limit: number = 50
): Promise<ItemSuggestions> {
  const empty: ItemSuggestions = { items: [], total: 0 };
  try {
    const response = await fetch("/v1/search/item/suggestions", {
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
