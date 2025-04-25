export class ModelComment {
    id: string;
    user: string;
    host: string
    timestamp: string;
    message: string;

    constructor(comment: ModelComment) {
        this.id = comment.id;
        this.user = comment.user;
        this.host = comment.host;
        this.timestamp = comment.timestamp;
        this.message = comment.message;
    }
}