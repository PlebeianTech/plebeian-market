import type { IEntity } from "$lib/types/base";

export class Order implements IEntity {
    key: string = "";
    endpoint = "orders";
    uuid: string = "";
    total_usd: number = 0;
    total: number = 0;
    on_chain_address: string = "";
    requested_at: Date | null = null;
    paid_at: Date | null = null;
    shipped_at: Date | null = null;
    expired_at: Date | null = null;
    canceled_at: Date | null = null;
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
        if (k === 'requested_at' || k === 'paid_at' || k === 'shipped_at' || k === 'expired_at' || k === 'canceled_at') {
            if (json[k] !== null) {
                o[k] = new Date(json[k]);
            } else {
                o[k] = null;
            }
        } else {
            o[k] = json[k];
        }
    }

    return o;
}
