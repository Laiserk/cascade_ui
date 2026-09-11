export interface QueryRequest {
    columns: string[];
    filter_expr: string | null;
    sort_expr: string | null;
    desc: boolean;
    offset: number;
    limit: number;
}

export interface QueryResponse {
    columns: string[];
    rows: Record<string, any>[];
    has_next: boolean;
    time_s: number;
    workspace_root: string;
    error: string | null;
}

export const DEFAULT_COLUMNS = ["path", "slug", "created_at"];
export const DEFAULT_LIMIT = 50;

const SHELL_SAFE = /^[A-Za-z0-9_.\-/]+$/;

function quote(token: string): string {
    if (SHELL_SAFE.test(token)) return token;
    return `'${token.replace(/'/g, `'\\''`)}'`;
}


//Renders the query the way it would be typed into a terminal
export function toCliCommand(req: QueryRequest): string {
    const parts = ["cascade query", ...req.columns.map(quote)];
    if (req.filter_expr) parts.push("filter", quote(req.filter_expr));
    if (req.sort_expr) {
        parts.push("sort", quote(req.sort_expr));
        if (req.desc) parts.push("desc");
    }
    if (req.offset) parts.push("offset", String(req.offset));
    parts.push("limit", String(req.limit));
    return parts.join(" ");
}
