import type {Model} from "@/models/Model";

export class Line {
    name: string;
    len: number;
    type: string;
    created_at: string;
    updated_at: string;
    models: Model[];

    constructor(line: Line) {
        this.name = line.name;
        this.len = line.len;
        this.type = line.type;
        this.created_at = line.created_at;
        this.updated_at = line.updated_at;
        this.models = line.models;
    }
}