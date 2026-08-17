import type { RouteLocationRaw } from "vue-router";

export type Type = "repo" | "model_line" | "data_line" | "model" | "dataset";

export interface NavSuggestion {
    type: Type;
    path: string;
    repo: string;
    line: string | null;
    name: string | null;
    num: number | null;
    slug: string | null;
    len: number | null;
}

export interface NavSuggestions {
    items: NavSuggestion[];
    total: number;
}

export const NAV_KIND_LABELS: Record<Type, string> = {
    repo: "repo",
    model_line: "line",
    data_line: "data line",
    model: "model",
    dataset: "dataset",
};


export function navRoute(item: NavSuggestion): RouteLocationRaw {
    switch (item.type) {
        case "repo":
            return { name: "repo", params: { repoName: item.repo } };
        case "model_line":
            return {
                name: "model_line",
                params: { repoName: item.repo, lineName: item.line as string },
            };
        case "data_line":
            return {
                name: "data_line",
                params: { repoName: item.repo, lineName: item.line as string },
            };
        case "model":
            return {
                name: "model",
                params: {
                    repoName: item.repo,
                    lineName: item.line as string,
                    modelNumString: item.name as string,
                },
            };
        case "dataset":
            return {
                name: "dataset",
                params: {
                    repoName: item.repo,
                    lineName: item.line as string,
                    datasetVer: item.name as string,
                },
            };
    }
}


export function isExactMatch(query: string, item: NavSuggestion): boolean {
    const normalized = query.trim().replace(/^\/+|\/+$/g, "").toLowerCase();
    if (!normalized) return false;
    return (
        normalized === item.path.toLowerCase() ||
        (item.slug !== null && normalized === item.slug.toLowerCase())
    );
}

export function navSubtitle(item: NavSuggestion): string {
    switch (item.type) {
        case "repo":
            return `repo • ${item.len} line(s)`;
        case "model_line":
            return `line • ${item.len} model(s)`;
        case "data_line":
            return `data line • ${item.len} dataset(s)`;
        case "model":
            return item.slug ?? "model • no slug, addressed by path";
        case "dataset":
            return `dataset • version ${item.name}`;
    }
}
