import type { ModelLine } from "@/models/ModelLine";

export async function fetchLineItems(
  repoName: string,
  lineName: string,
  selectedFields: string[],
  line: ModelLine,
  defaultFields: string[]
) {
  if (!repoName || !lineName) return;
  const fields = Array.from(new Set(selectedFields));
  const response = await fetch("/v1/line_item_table", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      line_path: { repo: repoName, line: lineName },
      item_fields: fields,
    }),
  });
  if (response.ok) {
    const items = await response.json();
    if (line) {
      // Merge fetched fields into existing items, preserving other fields
      if (!Array.isArray(line.items)) {
        line.items = [];
      }
      for (let idx = 0; idx < items.length; idx++) {
        const fetchedItem = items[idx] as Record<string, any>;
        let existing = (line.items[idx] as Record<string, any>) || {};
        // Merge fetched fields into existing item
        for (const field of Object.keys(fetchedItem)) {
          existing[field] = fetchedItem[field];
        }
        // Ensure defaultFields exist
        for (const field of defaultFields) {
          if (!(field in existing)) {
            existing[field] = "";
          }
        }
        // Cast back to the expected type for line.items
        line.items[idx] = existing as typeof line.items[number];
      }
      // If there are more existing items than fetched, keep the rest as is
      // If there are fewer, trim the array
      line.items.length = items.length;
    }
  }
}