export interface LineSuggestion {
    path: string;
    repo: string;
    line: string;
    type: string;
    len: number;
}

export interface LineSuggestions {
    items: LineSuggestion[];
    total: number;
}

export interface PlotPoint {
    num: number;
    slug: string | null;
    values: Record<string, any>;
}

export interface PlotSeries {
    id: string;
    path: string;
    repo: string;
    line: string;
    points: PlotPoint[];
    plot_fields: string[];
}

export interface PlotResponse {
    series: PlotSeries[];
    plot_fields: string[];
    not_found: string[];
}

export function lineId(line: LineSuggestion | PlotSeries): string {
    return line.path;
}
