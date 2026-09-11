import type { CompareResponse } from "@/models/Compare";

export default async function GetCompareTable(
  items: string[],
  itemFields: string[]
): Promise<CompareResponse> {
  const empty: CompareResponse = { columns: [], item_fields: [], not_found: [] };
  try {
    const response = await fetch("/v1/compare_item_table", {
      method: "post",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: items, item_fields: itemFields })
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
