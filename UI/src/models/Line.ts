import type {Model} from "@/models/Model";

export class Line {
    name: string;
    len: number;
    models: Model[];

    constructor(line: Line) {
        this.name = line.name;
        this.len = line.len;
        this.models = line.models;
    }
}