export class Workspace {
    name: string | null;
    len: number | null;
    repos: Repo[] | null

    constructor(workspace: Workspace) {
        this.name = workspace.name;
        this.len = workspace.len;
        this.repos = workspace.repos === null ? null : workspace.repos.map((item: Repo) => new Repo(item));
    }
}