import {Line, Response} from "@/models/Line";


export class ModelLine extends Line {
    items: Response[];

    constructor(line: ModelLine) {
        super(line);
        this.items = line.items;
    }
}