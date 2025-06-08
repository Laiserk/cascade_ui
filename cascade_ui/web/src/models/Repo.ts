import {ItemComment} from "@/models/ItemComment";

class LineRow {
    name: string;
    len: number;
    type: string;
    tags: string[];
    created_at: string;
    updated_at: string;

    constructor(lineRow: LineRow) {
        this.name = lineRow.name;
        this.len = lineRow.len;
        this.type = lineRow.type;
        this.tags = lineRow.tags;
        this.created_at = lineRow.created_at;
        this.updated_at = lineRow.updated_at;
    }
}

export class Repo {
    name: string;
    len: number;
    lines: LineRow[];
    tags: string[];
    comments: ItemComment[];

    constructor(repo: Repo) {
        this.name = repo.name;
        this.len = repo.len;
        this.lines = repo.lines.map(line => new LineRow(line));
        this.tags = repo.tags;
        this.comments = repo.comments.map(item => new ItemComment(item));
    }
}