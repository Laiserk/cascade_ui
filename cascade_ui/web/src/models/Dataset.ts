import type {ItemComment} from "@/models/ItemComment";

export class Dataset {
    name: string;
    path: string;
    saved_at: string;
    user: string;
    host: string;
    cwd: string;
    python_version: string;
    description: string;
    comments: ItemComment[];
    tags: string[];
    git_commit: string | null;
    git_uncommitted_changes: string[]

    constructor(model: Dataset) {
        this.name = model.name;
        this.path = model.path;
        this.saved_at = model.saved_at;
        this.user = model.user;
        this.host = model.host;
        this.cwd = model.cwd;
        this.python_version = model.python_version;
        this.description = model.description;
        this.comments = model.comments;
        this.tags = model.tags;
        this.git_commit = model.git_commit;
        this.git_uncommitted_changes = model.git_uncommitted_changes;
    }
}
