export class LogResponse {
    log_text: string | null;

    constructor(log: LogResponse) {
        this.log_text = log.log_text
    }
}