export interface ShoppingCartItem {
    id: string
    name: string;
    description: string;
    price: number;
    currency: string;
    image: string;
    quantity: number;
    orderQuantity: number;
    createdAt: number;
    stall_id: string;
    merchantPubkey: string;
}

export type stallOrder = {
    id: string,
    type: 0,
    name?: string,
    address?: string,
    message?: string,
    contact: {
        nostr?: string,
        phone?: string,
        email?: string,
    },
    items: [
        {
            product_id: string,
            quantity: number
        }
    ]
}
