<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {NostrGlobalConfig, isSuperAdmin} from "$sharedLib/stores";
    import AdminActions from "$lib/components/pagebuilder/AdminActions.svelte";
    import {EVENT_KIND_AUCTION} from "$sharedLib/services/nostr";
    import Countdown from "$sharedLib/components/Countdown.svelte";

    export let product;
    export let onImgError = () => {};

    let now = Math.floor(Date.now() / 1000);
    let endsAt = product.start_date + product.duration;
    let ended = now > endsAt;
</script>

<div class="relative grid h-[40rem] w-full max-w-[28rem] flex-col items-end justify-center overflow-hidden rounded-xl bg-white bg-clip-border text-center text-gray-700">
    <a class="cursor-pointer hover:underline" href="/product/{product.id}">
        <div class="absolute inset-0 m-0 h-full w-full overflow-hidden rounded-none bg-transparent bg-cover bg-clip-border bg-center text-gray-700 shadow-none"
             style="background-image: url('{product.images ? product.images[0] : product.image ?? productImageFallback}');">
            <div class="absolute bottom-0 left-0 right-0 h-30 bg-black bg-opacity-30 backdrop-blur text-white p-4 rounded-b-lg">

                    <h1 class="text-2xl font-semibold">{product.name}</h1>
                    {#if product.event.kind === EVENT_KIND_AUCTION}
                        <div class="p-5">
                            <Countdown totalSeconds={endsAt - now} bind:ended={ended} />
                        </div>
                    {:else}
                        <p class="mt-2 text-lg">{#if product.price}{product.price.toString().trim()} {#if product.currency}{product.currency.trim()}{/if}{/if}</p>
                    {/if}

                {#if $isSuperAdmin && $NostrGlobalConfig}
                    <a href={null} on:click|preventDefault>
                        <div class="p-4 pb-0 cursor-default">
                            <AdminActions
                                itemId={product.id}
                                entityName="products"
                            />
                        </div>
                    </a>
                {/if}
            </div>
        </div>
    </a>
</div>
