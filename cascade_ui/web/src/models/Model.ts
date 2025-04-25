import type {ModelComment} from "@/models/ModelComment";
import type {Metric} from "@/models/Metric";

export class Model {
    slug: string;
    path: string;
    created_at: string;
    saved_at: string;
    user: string;
    host: string;
    cwd: string;
    python_version: string;
    description: string;
    comments: ModelComment[];
    tags: string[];
    params: object;
    metrics: Metric[];
    artifacts: string[];
    files: string[];
    git_commit: string | null;
    git_uncommitted_changes: string[]

    constructor(model: Model) {
        this.slug = model.slug;
        this.path = model.path;
        this.created_at = model.created_at;
        this.saved_at = model.saved_at;
        this.user = model.user;
        this.host = model.host;
        this.cwd = model.cwd;
        this.python_version = model.python_version;
        this.description = model.description;
        this.comments = model.comments;
        this.tags = model.tags;
        this.params = model.params;
        this.metrics = model.metrics;
        this.artifacts = model.artifacts;
        this.files = model.files;
        this.git_commit = model.git_commit;
        this.git_uncommitted_changes = model.git_uncommitted_changes;
    }
}
