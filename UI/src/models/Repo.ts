export class Repo {
    name: string;
    len: number;

    constructor(repo: Repo) {
        this.name = repo.name;
        this.len = repo.len;
    }
}