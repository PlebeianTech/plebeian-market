<script lang="ts">
    import {formatTimestamp} from "$sharedLib/nostr/utils";
    import Countdown from "$sharedLib/components/Countdown.svelte";
    import {EVENT_KIND_AUCTION_BID, subscribeAuction} from "$sharedLib/services/nostr";
    import {Kind} from "nostr-tools";
    import {goto} from "$app/navigation";

    export let product;

    let now: number = 0;
    let endsAt: number = 0;
    let ended: boolean = false;
    let started: boolean = false;

    let bids = [];
    let sortedBids;
    let numBids: number = 0;
    let bidAmount: number = 0;

    let alreadySubscribedToReactions: boolean = false;

    $: if (product) {
        now = Math.floor(Date.now() / 1000);
        endsAt = product.start_date + product.duration;
        ended = now > endsAt;
        started = now > product.start_date;

        if (started && !ended && !alreadySubscribedToReactions && product.event.id) {
            alreadySubscribedToReactions = true;

//            console.log('SUBSCRIBING!!!', product.id);

            subscribeAuction([product.event.id],
                (auctionEvent) => {
                    if (auctionEvent.kind === EVENT_KIND_AUCTION_BID) {
                        console.log('************ bidEvent (bid)', auctionEvent);

                        bids[auctionEvent.id] = {
                            amount: Number(auctionEvent.content),
                            date: auctionEvent.created_at,
                            pubkey: auctionEvent.pubkey,
                            backendResponse: null
                        };

                        sortedBids = Object.entries(bids).sort((a, b) => {
                            return b[1].amount - a[1].amount;
                        });

                        console.log('   *** all the bids', bids);

                    } else if (auctionEvent.kind === Kind.Reaction) {
                        console.log('************ bidEvent (reaction)', auctionEvent);

                        sortedBids = Object.entries(bids).sort((a, b) => {
                            return b[1].amount - a[1].amount;
                        });

                        console.log('   *** all the bids', bids);
                    }
                });
        } else {
//            console.log('_NOT_ SUBSCRIBING', product.id);
        }
    }
</script>

{#if product && product.start_date}
    <div>
        {#if ended}
            <h3 class="text-xl text-center my-2">
                Auction ended at {formatTimestamp(endsAt, true)}
            </h3>

        {:else} <!-- not ended -->
            {#if started}
                <div class="pb-5">
                    <p class="mb-2">Auction ends in</p>
                    <Countdown totalSeconds={endsAt - now} bind:ended={ended} />
                </div>

                <div class="flex flex-wrap min-h-[6rem] min-w-[18rem] max-w-4xl gap-2 p-6 items-center justify-center overflow-x-hidden">
                    <div class="form-control">
                        <!--
                        <label class="label">
                            <span class="label-text">
                                {#if product.starting_bid && numBids === 0}
                                    Starting bid is {product.starting_bid}
                                {:else}
                                    Suggested bid
                                {/if}
                            </span>
                        </label>
                        <label class="input-group">
                            <input bind:value={bidAmount} type="number" name="bid-amount" id="bid-amount" class="input input-bordered w-full max-w-xs" />
                            <span class="text-base">sats</span>
                        </label>

                        <button class="btn btn-success mt-4" on:click|preventDefault={makeNewBid}>
                            Bid
                        </button>
                        -->
                    </div>
                </div>

                <!-- <BidList {sortedBids} {userProfileInfoMap} {openSitgBadgeInfo} /> -->

            {:else}
                Auction starts at {formatTimestamp(product.start_date, true)} and will run for {product.duration / 60} hours until {formatTimestamp(product.start_date + product.duration, true)}.
                <div class="divider"></div>
            {/if}

            <div class="mt-1 justify-end">
                <button class="btn btn-primary mt-4" on:click|preventDefault={() => goto('/product/' + product.id)}>
                    {#if started && !ended}
                        Bid
                    {:else}
                        View
                    {/if}
                </button>
            </div>
        {/if}
    </div>
{/if}
