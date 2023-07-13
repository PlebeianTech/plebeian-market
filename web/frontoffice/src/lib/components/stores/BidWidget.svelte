<script lang="ts">
    import {filterTags, formatTimestamp, queryNip05} from "$sharedLib/nostr/utils";
    import Countdown from "$lib/components/Countdown.svelte";
    import BidList from "$lib/components/stores/BidList.svelte";
    import {
        EVENT_KIND_AUCTION_BID,
        EVENT_KIND_AUCTION_BID_STATUS,
        sendMessage,
        subscribeAuction,
        subscribeMetadata,
        UserMetadata
    } from "$lib/services/nostr";
    import {NostrPublicKey} from "$sharedLib/stores";

    export let product;

    let now: number = 0;
    let endsAt: number = 0;
    let ended: boolean = false;
    let started: boolean = false;

    let bids = [];
    let sortedBids;
    let numBids: number = 0;
    let bidAmount: number = 0;

    let userProfileInfoMap = new Map<string, null | UserMetadata>();

    let alreadySubscribed: boolean = false;

    $: if (product) {
        now = Math.floor(Date.now() / 1000);
        endsAt = product.start_date + product.duration;
        ended = now > endsAt;
        started = now > product.start_date;

        setRecommendedBidAmount();

        if (!alreadySubscribed && product.event.id) {
            alreadySubscribed = true;

            subscribeAuction([product.event.id],
                (auctionEvent) => {
                    if (auctionEvent.kind === EVENT_KIND_AUCTION_BID) {

                        bids[auctionEvent.id] = {
                            amount: Number(auctionEvent.content),
                            date: auctionEvent.created_at,
                            pubkey: auctionEvent.pubkey,
                            backendResponse: null
                        };

                        sortedBids = Object.entries(bids).sort((a, b) => {
                            return b[1].amount - a[1].amount;
                        });

                        getUserMetadata(auctionEvent.pubkey);

                        setRecommendedBidAmount();

                    } else if (auctionEvent.kind === EVENT_KIND_AUCTION_BID_STATUS) {

                        if (auctionEvent.pubkey !== product.event.pubkey) {
                            console.error('WARNING! Someone tried to cheat on the auction, but we caught them!')
                            return;
                        }

                        try {
                            let bidResponse = JSON.parse(auctionEvent.content);

                            const eTags = filterTags(auctionEvent.tags, 'e');

                            for (let i = 0; i < eTags.length; i++) {
                                let tagValue = eTags[i][1];
                                if (product.event.id !== tagValue) {
                                    let bidInfo = bids[tagValue];

                                    if (bidResponse.status === 'winner' || (bidResponse.status !== 'winner' && bidInfo.backendResponse?.status !== 'winner' )) {
                                        if (bidResponse.status === 'winner') {
                                            const pTags = filterTags(auctionEvent.tags, 'p');
                                            for (let i = 0; i < pTags.length; i++) {
                                                bidResponse.winnerPubkey = pTags[i][1];
                                            }
                                        }

                                        bidInfo.backendResponse = bidResponse;
                                        bids[tagValue] = bidInfo;
                                    }
                                }
                            }

                            sortedBids = Object.entries(bids).sort((a, b) => {
                                return b[1].amount - a[1].amount;
                            });

                        } catch (error) { }
                    }
                });
        } else {
            setRecommendedBidAmount();
        }
    }

    function getUserMetadata(pubKey) {
        if (!userProfileInfoMap.has(pubKey)) {
            userProfileInfoMap.set(pubKey, null);

            subscribeMetadata(
                [pubKey],
                async (pk, userProfileInfo) => {
                    // nip-05 verification
                    if (userProfileInfo.nip05) {
                        let nip05verificationResult = await queryNip05(userProfileInfo.nip05);

                        if (nip05verificationResult !== null) {
                            if (pk === nip05verificationResult) {
                                let nip05Address = userProfileInfo.nip05;

                                if (nip05Address.startsWith('_@')) {
                                    userProfileInfo.nip05VerifiedAddress = nip05Address.substring(2);
                                } else {
                                    userProfileInfo.nip05VerifiedAddress = nip05Address;
                                }
                            }
                        }
                    }

                    userProfileInfoMap.set(pk, userProfileInfo);
                    userProfileInfoMap = userProfileInfoMap;    // For reactivity
                }
            );
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
    {#if ended}
        <h3 class="text-2xl text-center my-2">
            Auction ended at {formatTimestamp(endsAt, true)}
        </h3>

        <BidList {sortedBids} {userProfileInfoMap} />

    {:else} <!-- not ended -->
        {#if started}
            <div class="pb-5">
                <p class="mb-2">Auction ends in</p>
                <Countdown totalSeconds={endsAt - now} />
            </div>

            <div class="flex flex-wrap min-h-[6rem] min-w-[18rem] max-w-4xl gap-2 p-6 items-center justify-center overflow-x-hidden">
                <div class="form-control">
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
                </div>
            </div>

            <BidList {sortedBids} {userProfileInfoMap} />

        {:else}
            Auction starts at {formatTimestamp(product.start_date, true)} and will run for {product.duration / 60} hours until {formatTimestamp(product.start_date + product.duration, true)}.
            <div class="divider"></div>
        {/if}
    {/if}
{/if}
