export class ConfigResponse {
    config: object | null;
    overrides: object | null;

    constructor(cfg: ConfigResponse) {
        this.config = cfg.config;
        this.overrides = cfg.overrides;
    }
}