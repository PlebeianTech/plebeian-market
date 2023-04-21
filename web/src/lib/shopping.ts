import type {ShoppingCartItem} from "./types/stall";
import {Error, Info, ShoppingCart, stalls} from "./stores";
import { get } from 'svelte/store';
import productImageFallback from "$lib/images/product_image_fallback.svg";
import {getStalls} from "./services/nostr";
import type {SimplePool} from "nostr-tools";
import {getFirstTagValue} from "./nostr/utils";

// =============================== Products ====================================
export function onImgError(image) {
    image.onerror = "";
    image.src = productImageFallback;
}

// =============================== Shopping Cart ===============================
export function addToCart(addedProduct: ShoppingCartItem, orderQuantity) {
    if (orderQuantity > addedProduct.quantity) {
        Error.set('There are just ' + addedProduct.quantity + ' products in stock. You cannot order ' + orderQuantity);
        return false;
    }

    let productAdded = false;

    ShoppingCart.update(sc => {
        let stallMap: Map<string, Map<string, ShoppingCartItem>> = sc.products;

        let stall: Map<string, ShoppingCartItem> | undefined = stallMap.get(addedProduct.stall_id);
        if (stall === undefined) {
            // Stall doesn't exist. We create a product and put it in a new stall
            let product = new Map();
            addedProduct.orderQuantity = orderQuantity;
            product.set(addedProduct.id, addedProduct);
            stallMap.set(addedProduct.stall_id, product);
            productAdded = true;
        } else {
            // Stall exists. Does the item already exists?
            let product: ShoppingCartItem | undefined = stall.get(addedProduct.id);
            if (product === undefined) {
                addedProduct.orderQuantity = orderQuantity;
                stall.set(addedProduct.id, addedProduct);
                productAdded = true;
            } else {
                if ((product.orderQuantity + orderQuantity) > addedProduct.quantity) {
                    Error.set('There are just ' + addedProduct.quantity + ' products in stock. You already have ' + product.orderQuantity + ' on your shopping card, so you cannot order ' + orderQuantity + ' more.');
                } else {
                    product.orderQuantity = product.orderQuantity + orderQuantity;
                    productAdded = true;
                }
            }
        }

        if (productAdded) {
            Info.set('Product added to the shopping cart.');
        }

        return sc;
    });
}

export function deleteFromCart(stallId, productId) {
    ShoppingCart.update(sc => {
        let stallMap: Map<string, Map<string, ShoppingCartItem>> = sc.products;

        let stall = stallMap.get(stallId);

        if (stall !== undefined) {
            stall.delete(productId);

            if (stall.size === 0) {
                stallMap.delete(stallId);
            }
        }

        Info.set('Product removed from the shopping cart.');
        return sc;
    });
}

// =============================== Stalls ====================================

export function refreshStalls(NostrPool: SimplePool) {
    let now: number = Math.floor(Date.now());

    let currentStallsValue = get(stalls);

    if (currentStallsValue === null || now - currentStallsValue.fetched_at > 60000) {  // 60 seconds
        console.log('************ refreshStalls - refreshing...',)

        getStalls(NostrPool, null,
            (stallEvent) => {
                let content = JSON.parse(stallEvent.content)
                content.createdAt = stallEvent.created_at;
                content.merchantPubkey = stallEvent.pubkey;

                if (!content.id) {
                    let stallId = getFirstTagValue(stallEvent.tags, 'd');
                    if (stallId !== null) {
                        content.id = stallId;
                    } else {
                        return;
                    }
                }

                let stallId = content.id;

                // Get current value
                let currentStallsValue = get(stalls);

                if (currentStallsValue === null) {
                    currentStallsValue = {
                        stalls: {},
                        fetched_at: now
                    }
                } else {
                    currentStallsValue.fetched_at = now;
                }

                if (stallId in stalls) {
                    if (currentStallsValue.stalls[stallId].createdAt < stallEvent.created_at) {
                        currentStallsValue.stalls[stallId] = content;
                    }
                } else {
                    currentStallsValue.stalls[stallId] = content;
                }

                // Set new value
                stalls.set(currentStallsValue);
            });

    } else {
        console.log('************ refreshStalls - no need to refresh yet',)
    }
}
