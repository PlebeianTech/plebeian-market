import type {ShoppingCartItem} from "./types/stall";
import {Error, Info, ShoppingCart} from "./stores";
import productImageFallback from "$lib/images/product_image_fallback.svg";

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
