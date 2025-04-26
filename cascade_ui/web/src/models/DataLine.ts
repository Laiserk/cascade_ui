import {Line, Response} from "@/models/Line";


export class DataLine extends Line {
    items: Response[];

    constructor(line: DataLine) {
        super(line);
        this.items = line.items;
    }
}
