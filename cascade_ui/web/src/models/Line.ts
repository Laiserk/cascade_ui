import {ItemComment} from "@/models/ItemComment";

export class Response {
    name: string;
    slug: string;
    tags: string[];
    created_at: string;
    saved_at: string;

    constructor(model_response: Response) {
        this.name = model_response.name;
        this.slug = model_response.slug;
        this.tags = model_response.tags;
        this.created_at = model_response.created_at;
        this.saved_at = model_response.saved_at;
    }
}

export class Line {
    name: string;
    len: number;
    type: string;
    created_at: string;
    updated_at: string;
    items: Response[];
    item_fields: string[];
    tags: string[];
    comments: ItemComment[];
    plot_fields: string[];

    constructor(line: Line) {
        this.name = line.name;
        this.len = line.len;
        this.type = line.type;
        this.created_at = line.created_at;
        this.updated_at = line.updated_at;
        this.items = line.items;
        this.item_fields = line.item_fields;
        this.tags = line.tags;
        this.comments = line.comments;
        this.plot_fields = line.plot_fields;
    }
}