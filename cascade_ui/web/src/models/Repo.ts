import {Line} from "@/models/Line";
import {ItemComment} from "@/models/ItemComment";

export class Repo {
    name: string;
    len: number;
    lines: Line[];
    tags: string[];
    comments: ItemComment[];

    constructor(repo: Repo) {
        this.name = repo.name;
        this.len = repo.len;
        this.lines = repo.lines.map(line => new Line(line));
        this.tags = repo.tags;
        this.comments = repo.comments.map(item => new ItemComment(item));
    }
}