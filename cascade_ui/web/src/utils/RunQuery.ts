import type { QueryRequest, QueryResponse } from "@/models/Query";

export default async function RunQuery(request: QueryRequest): Promise<QueryResponse> {
  const empty: QueryResponse = {
    columns: request.columns,
    rows: [],
    has_next: false,
    time_s: 0,
    workspace_root: "",
    error: null
  };
  try {
    const response = await fetch("/v1/query", {
      method: "post",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request)
    });
    if (!response.ok) {
      return { ...empty, error: `Server responded with ${response.status}` };
    }
    return await response.json();
  } catch (error) {
    console.log(error);
    return { ...empty, error: String(error) };
  }
}
