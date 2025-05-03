import type {Metric} from "@/models/Metric";
import {Traceable} from "@/models/Traceable";

export class Model extends Traceable {
    slug: string;
    path: string;
    saved_at: string;
    params: object;
    metrics: Metric[];
    artifacts: string[];
    files: string[];

    constructor(model: Model) {
        super(model);
        this.slug = model.slug;
        this.path = model.path;
        this.saved_at = model.saved_at;
        this.params = model.params;
        this.metrics = model.metrics;
        this.artifacts = model.artifacts;
        this.files = model.files;
    }
}
