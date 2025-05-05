import {Traceable} from "@/models/Traceable";

export class Dataset extends Traceable {
    name: string;
    path: string;
    saved_at: string;

    constructor(dataset: Dataset) {
        super(dataset);
        this.name = dataset.name;
        this.path = dataset.path;
        this.saved_at = dataset.saved_at;
    }
}
