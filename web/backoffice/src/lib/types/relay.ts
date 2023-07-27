import type { IEntity } from "$lib/types/base";

export class Relay implements IEntity {
    url: string;

    key: string;
    endpoint = "relays";
    is_mine = false;

    constructor(url: string) {
        this.url = url;
        this.key = url;
    }

    public validate() {
        const colonIndex = this.url.indexOf(".");
        return !(this.url.length === 0) && colonIndex !== -1 && colonIndex !== this.url.length - 1;
    }

    public toJson() {
        return JSON.stringify({url: this.url});
    }
}

export function fromJson(json: any): Relay {
    return new Relay(<string>json.url);
}
