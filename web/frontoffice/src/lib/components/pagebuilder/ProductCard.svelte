<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {NostrGlobalConfig, isSuperAdmin} from "$sharedLib/stores";
    import { Image } from 'svelte-lazy-loader';
    import AdminActions from "$lib/components/pagebuilder/AdminActions.svelte";

    export let product;
    export let onImgError = () => {};
</script>

<div class="card w-full md:w-96 bg-base-200 dark:bg-base-300 shadow-xl mx-auto mb-4">
    <figure>
        <a class="cursor-pointer" href="/product/{product.id}">
            {#key `${product.id}-${product.images ? product.images[0] : product.image ?? productImageFallback}`}
                <Image
                    loading="lazy"
                    placeholder="{productImageFallback}"
                    src="{product.images ? product.images[0] : product.image ?? productImageFallback}" />
            {/key}
        </a>
    </figure>
    <div class="card-body items-center text-center p-4">
        {#if product.name}
            <span class="card-title md:text-lg">
                <a class="cursor-pointer hover:underline" href="/product/{product.id}">{product.name}</a>
            </span>
        {/if}

        {#if false && $isSuperAdmin && $NostrGlobalConfig}
            <AdminActions
                itemId={product.id}
                entityName="products"
            />
        {/if}
    </div>
</div>
