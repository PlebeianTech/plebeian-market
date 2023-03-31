<script lang="ts">
    import {Error} from "$lib/stores";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";
    import {shoppingCart} from "../../stores";

    export let product: string;
    export let onImgError = (image) => {
        image.onerror = "";
        image.src = profilePicturePlaceHolder;
    }

    function addToCart(merchant_id, product_id, total_quantity, quantity) {
        console.log('Adding to cart: ', merchant_id, total_quantity, product_id, quantity);

        if (quantity > total_quantity) {
            Error.set('There are just ' + total_quantity + ' items. You cannot order ' + quantity);
            return false;
        }

//        if ($shoppingCart.contains(merchant_id)) {
//            $shoppingCart[merchant_id][product_id]
//        } else {
            $shoppingCart[merchant_id] = [{
                'product_id': product_id,
                'quantity': quantity
            }];
//        }
    }
</script>

<tr>
    <td>{#if product.name}{product.name}{/if}</td>
    <td>{#if product.description}{product.description}{/if}</td>
    <td class="text-center">{product.quantity ?? 0}</td>
    <td class="text-center">{#if product.price}{product.price} {#if product.currency}({product.currency}){/if}{/if}</td>
    <td>
        <div class="card bg-base-100 shadow-xl w-full lg:w-32">
            <figure><img class="rounded-xl" src="{product.image ?? profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} /></figure>
        </div>
    </td>
    <td class="{!product.quantity ? 'tooltip tooltip-warning' : ''}" data-tip="Out of stock">
        <button class="btn btn-primary" class:btn-disabled={!product.quantity} on:click|preventDefault={() => addToCart('123415151', product.id, product.quantity, 3)}>
            Add to cart
        </button>
    </td>
    <td class="px-6 py-4">
        <div class="flex items-center space-x-3">
            <button class="inline-flex items-center p-1 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-full focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700" type="button">
                <span class="sr-only">Quantity button</span>
                <svg class="w-4 h-4" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>
            </button>
            <div>
                <input type="number" id="first_product" class="bg-gray-50 w-14 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block px-2.5 py-1 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="1" required>
            </div>
            <button class="inline-flex items-center p-1 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-full focus:outline-none hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-600 dark:focus:ring-gray-700" type="button">
                <span class="sr-only">Quantity button</span>
                <svg class="w-4 h-4" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd"></path></svg>
            </button>
        </div>
    </td>
</tr>
