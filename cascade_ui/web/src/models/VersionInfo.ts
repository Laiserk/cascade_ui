export class VersionInfo {
    cascade_ml_version: string;
    cascade_ui_version: string;

    constructor(info: VersionInfo) {
        this.cascade_ml_version = info.cascade_ml_version;
        this.cascade_ui_version = info.cascade_ui_version;
    }
}