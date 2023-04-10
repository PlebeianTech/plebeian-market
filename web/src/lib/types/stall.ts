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
