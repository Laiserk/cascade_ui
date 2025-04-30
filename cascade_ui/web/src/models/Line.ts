export class Response {
    name: string;
    slug: string;
    created_at: string;
    saved_at: string;

    constructor(model_response: Response) {
        this.name = model_response.name;
        this.slug = model_response.slug;
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

    constructor(line: Line) {
        this.name = line.name;
        this.len = line.len;
        this.type = line.type;
        this.created_at = line.created_at;
        this.updated_at = line.updated_at;
        this.items = line.items;
    }
}