import type {Repo} from "@/models/Repo";

export class Workspace {
    name: string;
    len: number;
    repos: Repo[] | null

    constructor(workspace: Workspace) {
        this.name = workspace.name;
        this.len = workspace.len;
        this.repos = workspace.repos === null ? null : workspace.repos.map((item) => item);
    }
}