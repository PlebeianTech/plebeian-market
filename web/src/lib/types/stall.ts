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
    stallId: string;
    merchantPubkey: string;
}
