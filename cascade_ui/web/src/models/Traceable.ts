import type {ItemComment} from "@/models/ItemComment";

export class Traceable {
    user: string;
    host: string;
    cwd: string;
    python_version: string;
    description: string;
    comments: ItemComment[];
    tags: string[];
    git_commit: string | null;
    git_uncommitted_changes: string[];
    created_at: string;

    constructor(traceable: Traceable) {
        this.user = traceable.user;
        this.host = traceable.host;
        this.cwd = traceable.cwd;
        this.python_version = traceable.python_version;
        this.description = traceable.description;
        this.comments = traceable.comments;
        this.tags = traceable.tags;
        this.git_commit = traceable.git_commit;
        this.git_uncommitted_changes = traceable.git_uncommitted_changes;
        this.created_at = traceable.created_at;
    }
}