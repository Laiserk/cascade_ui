export class Metric {
    name: string;
    value: number | null
    dataset: string | null
    split: string | null
    direction: string | null
    interval: [number, number] | null
    extra: object | null

    constructor(metric: Metric) {
        this.name = metric.name;
        this.value = metric.value;
        this.dataset = metric.dataset;
        this.split = metric.split;
        this.direction = metric.direction;
        this.interval = metric.interval;
        this.extra = metric.extra;
    }
}