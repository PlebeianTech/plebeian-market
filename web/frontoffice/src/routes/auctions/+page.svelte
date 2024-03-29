<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import {NostrPublicKey, privateMessages, stalls, Error, Info} from "$sharedLib/stores";
    import {getLastOrderContactInformation, onImgError, refreshStalls} from "$lib/shopping";
    import {afterNavigate, goto} from "$app/navigation";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import {waitAndShowLoginIfNotLoggedAlready} from "$sharedLib/utils";
    import {onDestroy, onMount} from "svelte";
    import ShippingContactInformation from "$lib/components/stores/ShippingContactInformation.svelte";
    import {filterTags} from "$sharedLib/nostr/utils";
    import {
        EVENT_KIND_AUCTION_BID,
        EVENT_KIND_AUCTION_BID_STATUS,
        getProducts,
        sendPrivateMessage,
        subscribeAuction
    } from "$sharedLib/services/nostr";
    import ShippingOptions from "$lib/components/stores/ShippingOptions.svelte";

    let name = null;
    let address = null;
    let message = null;

    let phone = null;
    let email = null;

    let auctionToOrder;
    let stallId;
    let product;
    let bids = [];
    let winnerBid = [];

    $: {
        let firstOneAdded = false;

        auctionToOrder = Object.entries($privateMessages.automatic)
            .filter(([, automaticMessage]) => {
                if (!firstOneAdded && automaticMessage.type === 10) {
                    const product_id = automaticMessage.items[0].product_id;

                    if (product_id) {
                        firstOneAdded = true;

                        // If valid ID, get product information
                        getProducts(null, [product_id],
                            (newProductInfo) => {
                                if (!product || (product && newProductInfo.event.created_at > product.event.created_at)) {
                                    product = newProductInfo;

                                    stallId = newProductInfo.stall_id;

                                    // If valid Product, get bids information
                                    if (newProductInfo.event.id) {
                                        subscribeAuction([newProductInfo.event.id],
                                            (auctionEvent) => {
                                                if (auctionEvent.kind === EVENT_KIND_AUCTION_BID) {

                                                    if (bids[auctionEvent.id] === undefined) {
                                                        bids[auctionEvent.id] = {};
                                                    }

                                                    bids[auctionEvent.id].amount = Number(auctionEvent.content);
                                                    bids[auctionEvent.id].date = auctionEvent.created_at;
                                                    bids[auctionEvent.id].pubkey = auctionEvent.pubkey;

                                                    if (!bids[auctionEvent.id].backendResponse) {
                                                        bids[auctionEvent.id].backendResponse = null;
                                                    }

                                                } else if (auctionEvent.kind === EVENT_KIND_AUCTION_BID_STATUS) {
                                                    if (auctionEvent.pubkey !== newProductInfo.event.pubkey) {
                                                        console.error('WARNING! Someone tried to cheat on the auction, but we caught them!')
                                                        return;
                                                    }

                                                    try {
                                                        let bidResponse = JSON.parse(auctionEvent.content);

                                                        if (bidResponse.status === 'winner') {
                                                            const eTags = filterTags(auctionEvent.tags, 'e');

                                                            for (let i = 0; i < eTags.length; i++) {
                                                                let tagValue = eTags[i][1];
                                                                if (newProductInfo.event.id !== tagValue) {
                                                                    if (bids[tagValue] === undefined) {
                                                                        bids[tagValue] = {
                                                                            backendResponse: null
                                                                        };
                                                                    }

                                                                    let bidInfo = bids[tagValue];

                                                                    const pTags = filterTags(auctionEvent.tags, 'p');
                                                                    for (let i = 0; i < pTags.length; i++) {
                                                                        bidResponse.winnerPubkey = pTags[i][1];
                                                                    }

                                                                    // Bid extended information
                                                                    bidInfo.backendResponse = bidResponse;
                                                                    bids[tagValue] = bidInfo;
                                                                }
                                                            }

                                                            winnerBid = Object.entries(bids)
                                                                .filter(([, bid]) => {
                                                                    if (bid.backendResponse === null) {
                                                                        return false;
                                                                    }

                                                                    return bid.backendResponse.status === 'winner' && bid.backendResponse.winnerPubkey === $NostrPublicKey;
                                                                });
                                                        }

                                                    } catch (error) {
                                                        console.error('Error parsing bid response:', error);
                                                    }
                                                }
                                            });
                                    }
                                }
                            });

                        return true;
                    }
                }

                return false;
            });
    }

    export async function buyNow() {
        console.log('---- buyNow start ----');

        if (!await waitAndShowLoginIfNotLoggedAlready()) {
            return;
        }

        if ($stalls.stalls[stallId].shippingOption === '0') {
            Error.set('You must choose shipping options for each order.');
            return;
        }

        // If there is no shippingOption chosen by the user and there is only
        // one shipping option, it's because we didn't even show the list to
        // the user, so let's auto-choose the only shipping option available
        if (!$stalls.stalls[stallId].shippingOption && $stalls.stalls[stallId].shipping.length === 1) {
            $stalls.stalls[stallId].shippingOption = $stalls.stalls[stallId].shipping[0].id;
        }

        let order = {
            id: auctionToOrder[0][0],
            stall_id: stallId,
            type: 0,
            contact: {
                nostr: $NostrPublicKey
            },
            shipping_id: $stalls.stalls[stallId].shippingOption
        };

        if (name && name !== '') {
            order.name = name;
        }
        if (address && address !== '') {
            order.address = address;
        }
        if (message && message !== '') {
            order.message = message;
        }
        if (phone && phone !== '') {
            order.contact.phone = phone;
        }
        if (email && email !== '') {
            order.contact.email = email;
        }

        try {
            let messageOrder = JSON.stringify(order);
            console.log('************ jsonOrder:  ', order);

            await sendPrivateMessage($stalls.stalls[stallId].merchantPubkey, messageOrder, false,
                async (relay) => {
                    console.log('-------- Order accepted by relay:', relay);

                    await new Promise(resolve => setTimeout(resolve, 2000));

                    await goto('/orders');
                }
            );

            Info.set('Information sent to the seller.');

            console.log('---- buyNow end ----');

        } catch (e) {
            Error.set('There was an error trying to send the information for the auction. Check that you have a Nostr extension in the browser or you have generated the Nostr key correctly.');
            console.log('Error trying to create the order for the auction:', e);
        }
    }

    const nostrPublicKeyUnsubscribe = NostrPublicKey.subscribe(async nostrPublicKeyValue => {
        if (nostrPublicKeyValue) {
            const contactDetails = getLastOrderContactInformation();
            name = contactDetails.name ?? '';
            address = contactDetails.address ?? '';
            phone = contactDetails.phone ?? '';
            email = contactDetails.email ?? '';
        }
    });
    onDestroy(nostrPublicKeyUnsubscribe);

    onMount(async () => {
        refreshStalls();
    });

    afterNavigate(async () => {
        await waitAndShowLoginIfNotLoggedAlready();
    });
</script>

<svelte:head>
    <title>Auction information</title>
</svelte:head>

<Titleh1>Auction information</Titleh1>

{#if stallId && product && winnerBid.length > 0}
    <div class="md:grid justify-center md:mt-6 mb-10">
        {#if auctionToOrder[0][1].id}
            <p class="text-sm mb-2 justify-center">
                Auction #{auctionToOrder[0][1].id}
            </p>
        {/if}
        <table class="w-fit md:w-full rounded border border-gray-400">
            <thead>
                <tr class="text-center">
                    <th>Name</th>
                    <th>Image</th>
                    <th class="p-2">Winning bid</th>
                </tr>
            </thead>
            <tbody>
                <ShippingOptions {stallId} i={null} inAuctionView={true} auctionProduct={product} />

                <tr class="border-b border-gray-600 hover text-sm md:text-base text-center">
                    <td class="py-1">
                        <p class="pl-3 text-center">{#if product.name}{product.name}{/if}</p>
                    </td>
                    <td class="py-2 px-4">
                        <div class="card shadow-xl w-20 md:w-20">
                            <figure><img class="rounded-xl" src="{product.images ? product.images[0] : product.image ?? productImageFallback}" on:error={(event) => onImgError(event.srcElement)} /></figure>
                        </div>
                    </td>
                    <td class="py-1">
                        {#if winnerBid[0][1].amount}
                            <p class="pr-2 text-center">
                                {winnerBid[0][1].amount} sats
                            </p>
                        {/if}
                    </td>
                </tr>

            </tbody>
        </table>
    </div>

    <ShippingContactInformation
        bind:name={name}
        bind:address={address}
        bind:message={message}
        bind:email={email}
        bind:phone={phone}
        {buyNow}
        isAuction={true}
    />

{:else}
    <div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-20 place-content-center">
        <div class="p-6 text-lg">
            <p>You didn't win any auction yet that you must provide information for.</p>
            <p class="mt-4">You can <a class="text-blue-500" href="/stalls">browse stalls</a> and buy some products.</p>
        </div>
    </div>
{/if}
