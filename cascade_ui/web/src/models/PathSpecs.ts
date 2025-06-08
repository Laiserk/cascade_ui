export class RepoPathSpec {
    repo: string;

    constructor(path: { repo: string }) {
        this.repo = path.repo;
    }
}

export class LinePathSpec extends RepoPathSpec {
    line: string;
    lineType: string;

    constructor(path: { repo: string; line: string; lineType: string }) {
        super(path)
        this.line = path.line;
        this.lineType = path.lineType;
    }
}

export class ModelPathSpec {
    repo: string;
    line: string;
    num: number;

    constructor(path: { repo: string; line: string; num: number }) {
        this.repo = path.repo;
        this.line = path.line;
        this.num = path.num;
    }
}
