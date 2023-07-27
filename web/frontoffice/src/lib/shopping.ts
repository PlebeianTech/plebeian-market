import type {ShoppingCartItem} from "./types/stall";
import {
    products,
    stalls
} from "./stores";
import {privateMessages, ShoppingCart, Error, Info} from "$sharedLib/stores";
import { get } from 'svelte/store';
import productImageFallback from "$lib/images/product_image_fallback.svg";
import {getProducts, getStalls} from "$lib/services/nostr";
import {filterTags, getFirstTagValue} from "../../../shared/src/lib/nostr/utils";

// =============================== Products ====================================
export function onImgError(image) {
    image.onerror = "";
    image.src = productImageFallback;
}

// =============================== Shopping Cart ===============================
export function addToCart(addedProduct: ShoppingCartItem, orderQuantity, saveToLocalStorage = true) {
    if (orderQuantity > addedProduct.quantity) {
        Error.set('There are just ' + addedProduct.quantity + ' products in stock. You cannot order ' + orderQuantity + '.');
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

        if (productAdded && saveToLocalStorage) {
            Info.set('Product added to the shopping cart.');
        }

        return sc;
    });

    if (saveToLocalStorage) {
        saveShoppingCartProductsToLocalStorage();
    }
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

    saveShoppingCartProductsToLocalStorage();
}

export function saveShoppingCartProductsToLocalStorage() {
    let products = [];

    for (const [stallId, stall] of get(ShoppingCart).products) {
        for (const [productId, product] of stall) {
            products.push(product);
        }
    }

    if (products.length > 0) {
        localStorage.setItem('shoppingCartProducts', JSON.stringify(products));
    } else {
        localStorage.removeItem('shoppingCartProducts');
    }
}

export function restoreShoppingCartProductsFromLocalStorage() {
    if (get(ShoppingCart).products.size !== 0) {
        console.debug("Shopping Cart is not empty, so we don't restore it", get(ShoppingCart));
        return;
    }

    const shoppingCartProducts = localStorage.getItem('shoppingCartProducts');

    if (shoppingCartProducts) {
        const parsedShoppingCartProducts = JSON.parse(shoppingCartProducts);

        for (const product of parsedShoppingCartProducts) {
            addToCart(product, product.orderQuantity, false)
        }
    }
}
// =============================== Stalls ====================================

export function refreshStalls() {
    let now: number = Math.floor(Date.now());

    let currentStallsValue = get(stalls);

    if (currentStallsValue === null || now - currentStallsValue.fetched_at > 60000) {  // 60 seconds
        console.log('************ refreshStalls - refreshing...',)

        getStalls(null,
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

                let stallId = content.id;

                if (stallId in currentStallsValue.stalls) {
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

export function getStallsByMerchant(merchantPubkey: string) {
    let merchantStalls = [];

    let allStalls = get(stalls);

    if (allStalls !== null) {
        Object.entries(allStalls.stalls).forEach(([stallId, stall]) => {
            if (merchantPubkey === stall.merchantPubkey) {
                merchantStalls[stallId] = stall;
            }
        });
    }

    return merchantStalls;
}

export function refreshProducts() {
    let now: number = Math.floor(Date.now());

    let currentProductsValue = get(products);

    if (currentProductsValue === null || now - currentProductsValue.fetched_at > 60000) {  // 60 seconds
        console.log('************ refreshProducts - refreshing...',)

        getProducts(null, null,
            (productEvent) => {
                let content = JSON.parse(productEvent.content);

                if (!content.id) {
                    let productId = getFirstTagValue(productEvent.tags, 'd');
                    if (productId === null) {
                        return;
                    }

                    content.id = productId;
                }

                content.createdAt = productEvent.created_at;
                content.merchantPubkey = productEvent.pubkey;

                let categoryTags = filterTags(productEvent.tags, 't');
                if (categoryTags.length > 0) {
                    categoryTags.forEach((category) => {
                        let tag = category[1].trim().toLowerCase();

                        // vitamin the product with tags
                        if (content.tags) {
                            content.tags.push(tag);
                        } else {
                            content.tags = [tag];
                        }
                    });
                }


                // Get current value
                let currentProductsValue = get(products);

                if (currentProductsValue === null) {
                    currentProductsValue = {
                        products: {},
                        fetched_at: now
                    }
                } else {
                    currentProductsValue.fetched_at = now;
                }

                let productId = content.id;

                if (productId in currentProductsValue.products) {
                    if (currentProductsValue.products[productId].createdAt < productEvent.created_at) {
                        currentProductsValue.products[productId] = content;
                    }
                } else {
                    currentProductsValue.products[productId] = content;
                }

                // Set new value
                products.set(currentProductsValue);
            });

    } else {
        console.log('************ refreshProducts - no need to refresh yet',)
    }
}

// =============================== Orders ====================================

export function getLastOrderContactInformation() {
    let contactDetails = {};

    const privateMessagesAutomatic = get(privateMessages).automatic;

    Object.entries(privateMessagesAutomatic).forEach(([messageId, privateMessage]) => {
        if (!privateMessage.paid) {     // So it's type === 1, but NostrMarket is not sending the type yet
            if (privateMessage.name) {
                contactDetails.name = privateMessage.name;
            }
            if (privateMessage.address) {
                contactDetails.address = privateMessage.address;
            }

            if (privateMessage.contact?.phone) {
                contactDetails.phone = privateMessage.contact.phone;
            }
            if (privateMessage.contact?.email) {
                contactDetails.email = privateMessage.contact.email;
            }
        }
    });

    return contactDetails;
}
