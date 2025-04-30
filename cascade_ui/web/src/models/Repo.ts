import {Line} from "@/models/Line";

export class Repo {
    name: string;
    len: number;
    lines: Line[];

    constructor(repo: Repo) {
        this.name = repo.name;
        this.len = repo.len;
        this.lines = repo.lines.map(line => new Line(line));
    }
}