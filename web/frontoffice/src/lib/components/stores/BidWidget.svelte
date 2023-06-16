<script lang="ts">
    import {formatTimestamp} from "$lib/nostr/utils";
    import Countdown from "$lib/components/Countdown.svelte";
    import {EVENT_KIND_AUCTION_BID, sendMessage, subscribeAuction} from "$lib/services/nostr";
    import {Kind} from "nostr-tools";
    import BidList from "$lib/components/stores/BidList.svelte";

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
        product.start_date = 1686646256;
        product.duration = 344000;   // 4 hours

        now = Math.floor(Date.now() / 1000);
        endsAt = product.start_date + product.duration;
        ended = now > endsAt;
        started = now > product.start_date;

        console.log('product.start_date:', product.start_date);
        console.log('product.duration:', product.duration);
        console.log('now:', now);
        console.log('endsAt:', product.start_date + product.duration);

        setRecommendedBidAmount();

        if (!alreadySubscribedToReactions && product.event.id) {
            alreadySubscribedToReactions = true;

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

                        setRecommendedBidAmount();

                        console.log('   *** all the bids', bids);

                    } else if (auctionEvent.kind === Kind.Reaction) {
                        console.log('************ bidEvent (reaction)', auctionEvent);



                        sortedBids = Object.entries(bids).sort((a, b) => {
                            return b[1].amount - a[1].amount;
                        });

                        setRecommendedBidAmount();

                        console.log('   *** all the bids', bids);
                    }
                });
        } else {
            setRecommendedBidAmount();
        }
    }

    function makeNewBid() {
        console.log('bidAmount', bidAmount);

        sendMessage('' + bidAmount, null, product.event, EVENT_KIND_AUCTION_BID,
            () => {
                console.log('Bid received by relay')
            });
    }

    function setRecommendedBidAmount() {
        numBids = Object.entries(bids).length;

        if (product.starting_bid && numBids === 0) {
            bidAmount = product.starting_bid;
        } else {
            if (numBids === 0) {
                bidAmount = 100;
            } else {
                let maxBid = sortedBids[0][1].amount;
                bidAmount = maxBid + Math.round(maxBid * 0.1);
            }
        }
    }
</script>

{#if product && product.start_date}
    {(console.log('product', product), '')}

    {#if ended}
        <h3 class="text-2xl text-center my-2">
            Auction ended at {formatTimestamp(endsAt, true)}
        </h3>

        <BidList {sortedBids} />

    {:else} <!-- not ended -->
        {#if started}
            <div class="pb-5">
                <p class="mb-2">Auction ends in</p>
                <Countdown totalSeconds={endsAt - now} />
            </div>

            <div class="form-control justify-center">
                <label class="label justify-center" for="bid-amount">
                    <span class="label-text justify-center">
                        {#if product.starting_bid && numBids === 0}
                            Starting bid is {product.starting_bid}
                        {:else}
                            Suggested bid
                        {/if}
                    </span>
                </label>
                <input bind:value={bidAmount} type="number" name="bid-amount" id="bid-amount" class="input input-bordered w-full max-w-xs" />
                <label class="label">
                    <span class="label-text-alt">sats</span>
                </label>
                <button class="btn btn-success mt-4" on:click|preventDefault={makeNewBid}>
                    Bid
                </button>
            </div>

            <BidList {sortedBids} />

        {:else}
            Auction starts at {formatTimestamp(product.start_date, true)} and will run for {product.duration / 60} hours until {formatTimestamp(product.start_date + product.duration, true)}.
            <div class="divider"></div>
        {/if}
    {/if}

    <!--
    <div>
        Started: {started}
        Ended: {ended}
    </div>
    -->
{/if}
