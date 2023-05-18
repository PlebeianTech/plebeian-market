import type { IEntity } from "$lib/types/base";
import type { IAccount } from "$lib/types/user";

export class Order implements IEntity {
    key: string = "";
    endpoint = "orders";
    total_usd: number = 0;
    total: number = 0;
    payment_address: string = "";
    requested_at?: Date = undefined;
    txid: string | null = null;
    tx_value?: number = undefined;
    is_mine = true;

    public validate() {
        return false; // since we cannot create orders from the UI
    }

    public toJson() {
        return null; // since orders are read-only
    }
}

export function fromJson(json: any): Order {
    var o: Order = new Order();

    for (var k in json) {
        if (k === 'requested_at') {
            o[k] = new Date(json[k]);
        } else {
            o[k] = json[k];
        }
    }

    return o;
}
