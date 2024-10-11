export class Repo {
    name: string | null;
    len: number | null;

    constructor(repo: Repo) {
        this.name = repo.name;
        this.len = repo.len;
    }
}