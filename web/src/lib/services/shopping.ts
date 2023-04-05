import type {ShoppingCartItem} from "../types/nip45";
import {Error, Info, ShoppingCart} from "../stores";
import productImageFallback from "$lib/images/product_image_fallback.svg";

// =============================== Products ====================================
export function onQtyChangeClick(event, plus = false) {
    let parentOfClickedButton = event.srcElement.parentElement.parentElement.parentElement;

    const quantitySelector = parentOfClickedButton.getElementsByClassName('quantitySelector');

    if (quantitySelector.length !== 1) {
        Error.set('There was an error trying to modify the quantity.');
        return;
    }

    let actualValue = Number(quantitySelector[0].value);

    let newValue = plus ? ++actualValue : --actualValue;

    if (newValue === 0 && plus === false) {
        return;
    }

    quantitySelector[0].value = newValue;
}

export function onImgError(image) {
    image.onerror = "";
    image.src = productImageFallback;
}

// =============================== Shopping Cart ===============================
export function addToCart(added_product: ShoppingCartItem, event) {
    // console.log('Adding to cart: ', product, event);
    const addToCartButton = event.srcElement;

    const quantitySelector = addToCartButton.parentNode.getElementsByClassName('quantitySelector');
    if (quantitySelector.length !== 1) {
        Error.set('There was an error trying to get the amount you want to buy.');
        return;
    }

    const quantitySelectorValue = Number(quantitySelector[0].value);

    if (quantitySelectorValue > added_product.quantity) {
        Error.set('There are just ' + added_product.quantity + ' products. You cannot order ' + quantitySelectorValue);
        return false;
    }

    // Vitamin the product object
    added_product.orderQuantity = quantitySelectorValue;

    ShoppingCart.update(sc => {
        let stallMap: Map<string, Map<string, ShoppingCartItem>> = sc.products;

        let stall: Map<string, ShoppingCartItem> | undefined = stallMap.get(added_product.stall_id);
        if (stall === undefined) {
            // Stall doesn't exist. We create a product and put it in a new stall
            let product = new Map();
            product.set(added_product.id, added_product);
            stallMap.set(added_product.stall_id, product);
        } else {
            // Stall exists. Does the item already exists?
            let product: ShoppingCartItem | undefined = stall.get(added_product.id);
            if (product === undefined) {
                stall.set(added_product.id, added_product);
            } else {
                console.log('product.orderQuantity: ' + product.orderQuantity + ' - added_product.orderQuantity: ' + added_product.orderQuantity);
                product.orderQuantity = product.orderQuantity + added_product.orderQuantity;
            }
        }

        Info.set('Product added to the shopping cart.');
        return sc;
    });
}

export function deleteFromCart(stall_id, product_id) {
    ShoppingCart.update(sc => {
        let stallMap: Map<string, Map<string, ShoppingCartItem>> = sc.products;

        let stall = stallMap.get(stall_id);

        if (stall !== undefined) {
            stall.delete(product_id);

            if (stall.size === 0) {
                stallMap.delete(stall_id);
            }
        }

        Info.set('Product removed from the shopping cart.');
        return sc;
    });
}
