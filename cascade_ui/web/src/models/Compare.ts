export interface ItemSuggestion {
    path: string;
    repo: string;
    line: string;
    name: string;
    num: number;
    slug: string | null;
}

export interface ItemSuggestions {
    items: ItemSuggestion[];
    total: number;
}

export interface CompareColumn {
    id: string;
    path: string;
    repo: string;
    line: string;
    name: string;
    num: number;
    slug: string | null;
    meta: Record<string, any>;
    available_fields: string[];
}

export interface CompareResponse {
    columns: CompareColumn[];
    item_fields: string[];
    not_found: string[];
}

export function itemId(item: ItemSuggestion | CompareColumn): string {
    return item.slug ? item.slug : item.path;
}
