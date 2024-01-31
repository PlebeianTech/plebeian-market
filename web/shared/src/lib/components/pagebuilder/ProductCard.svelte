<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {NostrGlobalConfig, isSuperAdmin} from "$sharedLib/stores";
    import AdminActions from "$sharedLib/components/pagebuilder/AdminActions.svelte";
    import {EVENT_KIND_AUCTION} from "$sharedLib/services/nostr";
    import Countdown from "$sharedLib/components/Countdown.svelte";
    import CurrencyConverter from "$sharedLib/components/CurrencyConverter.svelte";

    export let product;
    export let onImgError = () => {};

    let now = Math.floor(Date.now() / 1000);
    let endsAt = product.start_date + product.duration;
    let ended = now > endsAt;
</script>

<div class="relative grid h-[40rem] max-h-48 md:max-h-[32rem] w-full max-w-[28rem] flex-col items-end justify-center overflow-hidden rounded-md md:rounded-xl bg-white bg-clip-border text-center text-gray-700">
    <a class="cursor-pointer hover:underline" href="/product/{product.id}">
        <div class="absolute inset-0 m-0 h-full w-full overflow-hidden rounded-none bg-transparent bg-cover bg-clip-border bg-center text-gray-700 shadow-none"
             style="background-image: url('{product.images ? product.images[0] : product.image ?? productImageFallback}');">
            <div class="absolute p-2 pt-1 md:p-4 bottom-0 left-0 right-0 h-30 bg-black bg-opacity-30 backdrop-blur text-white rounded-b-lg" class:pb-0={$isSuperAdmin}>
                <h1 class="text-md md:text-2xl leading-4">{product.name}</h1>
                {#if product.event.kind === EVENT_KIND_AUCTION}
                    <div class="p-5">
                        <Countdown totalSeconds={endsAt - now} bind:ended={ended} />
                    </div>
                {:else}
                    {#if product.price && product.currency}
                        <CurrencyConverter
                            amount={product.price}
                            sourceCurrency={product.currency}
                        />
                    {:else}
                        <p class="mt-1 md:mt-2 text-xs md:text-lg">{#if product.price}{product.price.toString().trim()} {#if product.currency}{product.currency.trim()}{/if}{/if}</p>
                    {/if}
                {/if}

                {#if $isSuperAdmin && $NostrGlobalConfig}
                    <a href={null} on:click|preventDefault>
                        <div class="p-0 md:p-4 md:pb-0 cursor-default">
                            <AdminActions
                                itemId={product.id}
                                entityName="products"
                                classOverride="text-white"
                                showAddActions={false}
                            />
                        </div>
                    </a>
                {/if}
            </div>
        </div>
    </a>
</div>
