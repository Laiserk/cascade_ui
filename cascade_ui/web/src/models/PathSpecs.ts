export class RepoPathSpec {
    repo: string;

    constructor(path: RepoPathSpec) {
        this.repo = path.repo;
    }
}

export class LinePathSpec extends RepoPathSpec {
    line: string;

    constructor(path: LinePathSpec) {
        super(path)
        this.line = path.line;
    }
}

export class ModelPathSpec extends LinePathSpec {
    num: number;

    constructor(path: ModelPathSpec) {
        super(path)
        this.num = path.num;
    }
}
