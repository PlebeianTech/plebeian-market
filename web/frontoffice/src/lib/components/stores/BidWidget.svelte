<script lang="ts">
    import {filterTags, formatTimestamp, queryNip05, sendSitgBadgeOrder} from "$sharedLib/nostr/utils";
    import Countdown from "$sharedLib/components/Countdown.svelte";
    import BidList from "$lib/components/stores/BidList.svelte";
    import {
        EVENT_KIND_AUCTION_BID,
        EVENT_KIND_AUCTION_BID_STATUS,
        sendMessage,
        subscribeAuction,
        subscribeMetadata
    } from "$sharedLib/services/nostr";
    import type {UserMetadata} from "$sharedLib/services/nostr";
    import {NostrPublicKey, privateMessages} from "$sharedLib/stores";
    import PaymentWidget from "$lib/components/stores/PaymentWidget.svelte";

    export let product;

    let now: number = 0;
    let endsAt: number = 0;
    let ended: boolean = false;
    let started: boolean = false;

    let totalTimeExtension: number = 0;

    let bids: object[] = [];
    let sortedBids;
    let numBids: number = 0;
    let numAcceptedBids: number = 0;
    let bidAmount: number = 0;
    $: higgerAcceptedBid = null;

    let didIBidOnThisProduct: boolean = false;

    let userProfileInfoMap = new Map<string, null | UserMetadata>();

    let alreadySubscribed: boolean = false;

    let badgeOrderToBePaid = null;
    let badgeOrderToBePaidId: string | null = null;
    let badgeModalIShouldBuy = false;
    let badgeModalPaying = false;

    let showPaymentDetails;

    $: if (product) {
        now = Math.floor(Date.now() / 1000);
        endsAt = product.start_date + product.duration + totalTimeExtension;
        ended = now > endsAt;
        started = now > product.start_date;

        setRecommendedBidAmount();

        if (!alreadySubscribed && product.event.id) {
            alreadySubscribed = true;

            subscribeAuction([product.event.id],
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
                            bidResponse.created_at = auctionEvent.created_at;

                            const eTags = filterTags(auctionEvent.tags, 'e');

                            for (let i = 0; i < eTags.length; i++) {
                                let tagValue = eTags[i][1];
                                if (product.event.id !== tagValue) {

                                    if (bids[tagValue] === undefined) {
                                        bids[tagValue] = {
                                            backendResponse: null
                                        };
                                    }

                                    let bidInfo = bids[tagValue];

                                    if (bidResponse.status === 'accepted' || bidResponse.status === 'winner') {
                                        // This kind of response always have priority, so let them go
                                    } else {
                                        if (!bidInfo.backendResponse || (bidInfo.backendResponse && bidInfo.backendResponse.created_at < bidResponse.created_at)) {
                                            // We don't yet have a response from backend, or the response we have
                                            // is older than this one. So this response is the latest one, let it go.
                                        } else {
                                            // We already have a response from backend, and it's newer than this one.
                                            // So let's ignore this one.
                                            return;
                                        }
                                    }

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

                                    if (bidResponse.status === 'accepted') {
                                        const timeToExtend = bidResponse.duration_extended;

                                        if (timeToExtend && timeToExtend > 0) {
                                            totalTimeExtension += timeToExtend;
                                        }
                                    }
                                }
                            }

                            sortedBids = Object.entries(bids).sort((a, b) => {
                                return b[1].amount - a[1].amount;
                            });

                        } catch (error) { }
                    }
                },
                null);
        } else {
            setRecommendedBidAmount();
        }
    }

    $: if (sortedBids && sortedBids.length > 0) {
        numAcceptedBids = 0;
        higgerAcceptedBid = null;

        sortedBids.forEach(([bidId, bidInfo]) => {
            if (bidInfo.backendResponse && bidInfo.backendResponse.status === 'accepted') {
                if (bidInfo.pubkey === $NostrPublicKey) {
                    didIBidOnThisProduct = true;
                }

                if (higgerAcceptedBid === null) {
                    higgerAcceptedBid = bidInfo;
                }

                numAcceptedBids++;
            }
        });
    }

    function getUserMetadata(pubKey) {
        if (!userProfileInfoMap.has(pubKey)) {
            userProfileInfoMap.set(pubKey, null);

            subscribeMetadata([pubKey],
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
                },
                () => {}
            );
        }
    }

    function makeNewBid() {
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

    $: {
        if (badgeOrderToBePaidId) {
            Object.entries($privateMessages.automatic).forEach(([orderId, order]) => {
                if (badgeOrderToBePaidId === orderId && order.type === 1) {
                    badgeOrderToBePaid = order;
                }
                if (badgeOrderToBePaidId === orderId && order.type === 2 && order.paid) {
                    closeSitgBadgeInfo();
                }
            });
        }
    }

    async function openSitgBadgeInfo(badgeStallId, badgeProductId, isCurrentUser) {
        resetEverything();

        badgeModalIShouldBuy = isCurrentUser;

        if (isCurrentUser) {
            badgeOrderToBePaidId = await sendSitgBadgeOrder(badgeStallId, badgeProductId);
        }

        window.skin_in_the_game_modal.showModal();
    }

    function closeSitgBadgeInfo() {
        window.skin_in_the_game_modal.close();
        resetEverything();
    }

    function resetEverything() {
        badgeOrderToBePaidId = null;
        badgeOrderToBePaid = null;
        badgeModalPaying = false;
    }
</script>

{#if product && product.start_date}
    {#if ended}
        <h3 class="text-2xl text-center my-2">
            Auction ended at {formatTimestamp(endsAt, true)}
        </h3>
    {:else} <!-- not ended -->
        {#if started}
            <div class="pb-5">
                <p class="mb-2">Auction ends in</p>
                <Countdown totalSeconds={endsAt - now} bind:ended={ended} />
                {#if totalTimeExtension > 0}
                    <div class="badge badge-info badge-lg mt-4">Time has been extended</div>
                    <div class="dropdown dropdown-hover">
                        <div tabindex="0" class="badge badge-error badge-md mt-4">?</div>
                        <ul tabindex="0" class="dropdown-content menu p-2 shadow bg-base-300 rounded-box w-52">
                            <li><a class="active">Time gets extended each time a new bid come in the last 5 minutes of the auction</a></li>
                        </ul>
                    </div>
                {/if}
            </div>

            <div class="p-3 pb-3">
                {#if numBids === 0}
                    This auction doesn't have any bid yet. Be the first to bid!
                {:else if numAcceptedBids === 0}
                    This auction doesn't have any accepted bid yet. Be the first to bid!
                {:else}
                    {#if didIBidOnThisProduct}
                        {#if higgerAcceptedBid && higgerAcceptedBid.pubkey === $NostrPublicKey}
                            <span class="font-bold">You're currently the top bidder!</span>
                        {:else}
                            <span class="font-bold">Somebody outbid you! Bid again to become the top bidder.</span>
                        {/if}
                    {/if}

                    {#if higgerAcceptedBid.backendResponse && !higgerAcceptedBid.backendResponse.reserve_bid_reached}
                        <p class="pt-9 font-bold">The reserve price hasn't been met yet.</p>
                        <p class="text-xs">The reserve price is the minimum price that the seller is willing to accept for the item.</p>
                    {/if}
                {/if}
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
        {:else}
            Auction starts at {formatTimestamp(product.start_date, true)} and will run for {product.duration / 60} hours until {formatTimestamp(product.start_date + product.duration, true)}.
            <div class="divider"></div>
        {/if}
    {/if}

    {#if !(!started && !ended)}
        <BidList {sortedBids} {userProfileInfoMap} {openSitgBadgeInfo} />
    {/if}
{/if}

<dialog id="skin_in_the_game_modal" class="modal">
    <div class="modal-box">
        {#if !badgeModalPaying}
            <h3 class="font-bold text-lg">Skin in the Game proof needed!</h3>
            <p class="py-4 text-base">Bidding for this auction has reached a threshold, and participants are required to complete a <b>"Skin In The Game"</b> test as an <b>anti-spam</b> measure.</p>
            {#if badgeModalIShouldBuy}
                <p class="py-4 text-base">You have to buy the Plebeian Market <b>"Skin In The Game"</b> badge which costs $20. This has to be done <b>just once</b>, and you'll be able to bid on as many auctions as you want.</p>
            {:else}
                <p class="py-4 text-base">The user that made the bid have to buy the Plebeian Market <b>"Skin In The Game"</b> badge.</p>
            {/if}
            <div class="h-64 inline-flex">
                <img class="mx-auto" src="/badges/skin-in-the-game.png" alt="Skin In The Game Badge" />
            </div>
            {#if badgeModalIShouldBuy}
                <p class="text-base">As soon as you have the badge, <b>your bid will be approved</b>.</p>
            {:else}
                <p class="text-base">As soon as the user buys the badge, <b>the bid will be approved</b>.</p>
            {/if}
        {:else}
            {#if badgeOrderToBePaid}
                <PaymentWidget {badgeOrderToBePaid} bind:showPaymentDetails={showPaymentDetails} />
            {/if}
        {/if}

        <div class="modal-action">
            {#if badgeModalIShouldBuy}
                {#if !badgeModalPaying}
                    <div class="inline-flex">
                        {#if badgeOrderToBePaid}
                            <button class="btn btn-primary" on:click|preventDefault={() => badgeModalPaying = true}>Buy badge</button>
                        {:else}
                            <button class="btn btn-success no-animation cursor-default" on:click|preventDefault={() => showPaymentDetails = true}>
                                <span class="loading loading-spinner"></span>
                                Preparing order...
                            </button>
                        {/if}
                    </div>
                {/if}
            {/if}

            <button class="btn mt-0" on:click={closeSitgBadgeInfo}>Close</button>
        </div>
    </div>
</dialog>
