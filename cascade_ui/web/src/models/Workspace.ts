import type {Repo} from "@/models/Repo";
import {ItemComment} from "@/models/ItemComment";

export class Workspace {
    name: string;
    len: number;
    repos: Repo[] | null;
    tags: string[];
    comments: ItemComment[];

    constructor(workspace: Workspace) {
        this.name = workspace.name;
        this.len = workspace.len;
        this.repos = workspace.repos === null ? null : workspace.repos.map((item) => item);
        this.tags = workspace.tags;
        this.comments = workspace.comments.map((item) => new ItemComment(item));
    }
}