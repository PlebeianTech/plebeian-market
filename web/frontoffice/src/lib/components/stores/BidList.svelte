<script lang="ts">
    import {formatTimestamp, sendSitgBadgeOrder} from "$sharedLib/nostr/utils";
    import profilePicturePlaceHolder from "$sharedLib/images/profile_picture_placeholder.svg";
    import Clock from "$sharedLib/components/icons/Clock.svelte";
    import WinnerBadge from "$sharedLib/components/icons/WinnerBadge.svelte";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";
    import {NostrPublicKey} from "$sharedLib/stores";

    export let sortedBids;
    export let userProfileInfoMap;

    const winnerColor = 'bg-green-300 dark:bg-[#446600]';

    function openSitgBadgeInfo(badgeStallId, badgeProductId, isCurrentUser) {
        if (isCurrentUser) {
            const orderId = sendSitgBadgeOrder(badgeStallId, badgeProductId);
            console.log('   ******************** orderId', orderId);
        }

        window.skin_in_the_game_modal.showModal();
    }
</script>

{#if sortedBids && sortedBids.length > 0}
    <div class="mt-8 mb-6">
        <!-- Mobile -->
        <table class="md:hidden w-full table table-fixed table-sm sm:table-md md:table-lg text-center">
            <thead>
                <tr class="text-lg">
                    <th class="pl-0">Bid</th>
                    <th class="pr-0">Info</th>
                </tr>
            </thead>
            <tbody>
            {#each sortedBids as [_, bid]}
                <tr class:bg-success={bid.backendResponse && bid.backendResponse.status === 'winner'}>
                    <th class="text-center {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">
                        {bid.amount} sats
                        <p class="mt-1">{formatTimestamp(bid.date)}</p>

                        <div class="mt-1">
                            {#if !bid.backendResponse}
                                <div class="w-8 h-8 mx-auto"><Clock /></div>
                                <p class="line-clamp-3 mt-1 whitespace-normal">
                                    Waiting response from marketplace
                                </p>
                            {:else}
                                {#if bid.backendResponse.status === 'accepted'}
                                    <div class="mx-auto tooltip" data-tip="Bid confirmed">✅</div>
                                {:else if bid.backendResponse.status === 'rejected'}
                                    <div class="mx-auto tooltip" data-tip="Bid rejected">❌</div>
                                    <p class="line-clamp-3 mt-1 whitespace-normal">
                                        {bid.backendResponse.message}
                                    </p>
                                {:else if bid.backendResponse.status === 'pending'}
                                    <div class="mx-auto tooltip" data-tip="Bid pending"><Clock /></div>
                                    <p class="line-clamp-3 mt-1 whitespace-normal">
                                        {#if bid.backendResponse.badge_stall_id}
                                            {#if bid.backendResponse.winnerPubkey === $NostrPublicKey}
                                                You need to pass the "<b>Skin in the Game</b>" process before the bid is accepted.
                                            {:else}
                                                "<b>Skin in the Game</b>" process needs to be done by this user before the bid is accepted.
                                            {/if}
                                            <button class="btn btn-sm btn-success" on:click|preventDefault={() => openSitgBadgeInfo(bid.backendResponse.badge_stall_id, bid.backendResponse.badge_product_id)}>See more details here</button>
                                            <label for="skin_in_the_game_modal" class="cursor-pointer underline">See more details here</label>.
                                        {:else}
                                            {bid.backendResponse.message}
                                        {/if}
                                    </p>
                                {:else if bid.backendResponse.status === 'winner'}
                                    <div class="w-8 h-8 mx-auto"><WinnerBadge /></div>
                                    <p class="line-clamp-3 mt-1 whitespace-normal">
                                        {#if bid.backendResponse.winnerPubkey === $NostrPublicKey}
                                            You're the winner!
                                        {:else}
                                            Winner
                                        {/if}
                                    </p>
                                {:else}
                                    Unknown response from the marketplace
                                {/if}
                            {/if}
                        </div>
                    </th>
                    <th class="{bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}r">
                        <div class="flex w-fit mx-auto mt-1 space-x-3 items-center">
                            <div class="avatar mask mask-squircle w-12 h-12">
                                <img src={userProfileInfoMap.get(bid.pubkey)?.picture ?? profilePicturePlaceHolder} alt="Avatar of the identity that made the bid" />
                            </div>
                            <div class="flex">
                                {#if userProfileInfoMap.get(bid.pubkey)}
                                    <span class="tooltip font-normal" data-tip="{bid.pubkey}">{userProfileInfoMap.get(bid.pubkey).name}</span>
                                    {#if userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}
                                        <span class="ml-1">
                                            <Nip05Checkmark address="{userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}" />
                                        </span>
                                    {/if}
                                {:else}
                                    <span class="tooltip" data-tip="{bid.pubkey}">{bid.pubkey.substring(0,6)}...</span>
                                {/if}
                            </div>
                        </div>
                    </th>
                </tr>
            {/each}
            </tbody>
        </table>

        <!-- Desktop -->
        <table class="hidden md:block table table-lg table-fixed w-max text-center">
            <thead>
                <tr class="text-sm">
                    <th>Bid</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Bidder</th>
                </tr>
            </thead>
            <tbody>
            {#each sortedBids as [_, bid]}
                <tr>
                    <th class="text-center {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}"><span class="p-3">{bid.amount} sats</span></th>
                    <td class="text-center {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">{formatTimestamp(bid.date)}</td>
                    <td class="text-center text-xs {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor : ''}">
                        {#if !bid.backendResponse}
                            <div class="w-8 h-8 mx-auto"><Clock /></div>
                            <p class="line-clamp-3 mt-1 whitespace-normal">
                                Waiting response from marketplace
                            </p>
                        {:else}
                            {#if bid.backendResponse.status === 'accepted'}
                                <div class="text-xl mx-auto tooltip" data-tip="Bid confirmed">✅</div>
                            {:else if bid.backendResponse.status === 'rejected'}
                                <div class="text-xl mx-auto tooltip" data-tip="Bid rejected">❌</div>
                                <p class="line-clamp-3 mt-1 whitespace-normal">
                                    {bid.backendResponse.message}
                                </p>
                            {:else if bid.backendResponse.status === 'pending'}
                                <div class="w-8 h-8 mx-auto text-xl tooltip" data-tip="Bid pending"><Clock /></div>
                                <p class="line-clamp-3 mt-1 whitespace-normal">
                                    {#if bid.backendResponse.badge_stall_id}
                                        {#if bid.backendResponse.winnerPubkey === $NostrPublicKey}
                                            You need to pass the "<b>Skin in the Game</b>" process before the bid is accepted.
                                        {:else}
                                            "<b>Skin in the Game</b>" process needs to be done by this user before the bid is accepted.
                                        {/if}
                                        <button class="btn btn-sm btn-success" on:click|preventDefault={() => openSitgBadgeInfo(bid.backendResponse.badge_stall_id, bid.backendResponse.badge_product_id)}>See more details here</button>
                                        <label for="skin_in_the_game_modal" class="cursor-pointer underline">See more details here</label>.
                                    {:else}
                                        {bid.backendResponse.message}
                                    {/if}
                                </p>
                            {:else if bid.backendResponse.status === 'winner'}
                                <div class="w-8 h-8 mx-auto"><WinnerBadge /></div>
                                <p class="line-clamp-3 mt-1 whitespace-normal font-bold">
                                    {#if bid.backendResponse.winnerPubkey === $NostrPublicKey}
                                        You're the winner!
                                    {:else}
                                        Winner
                                    {/if}
                                </p>
                            {:else}
                                Unknown response from the marketplace
                            {/if}
                        {/if}
                    </td>
                    <th class="{bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">
                        <div class="flex items-center space-x-3 p-3">
                            <div class="avatar mask mask-squircle w-12 h-12">
                                <img src={userProfileInfoMap.get(bid.pubkey)?.picture ?? profilePicturePlaceHolder} alt="Avatar of the identity that made the bid" />
                            </div>
                            <div class="flex">
                                {#if userProfileInfoMap.get(bid.pubkey)}
                                    <span class="tooltip" data-tip="{bid.pubkey}">{userProfileInfoMap.get(bid.pubkey).name ?? bid.pubkey.substring(0,6) + '...'}</span>
                                    {#if userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}
                                        <span class="mt-1 ml-2">
                                            <Nip05Checkmark address="{userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}" />
                                        </span>
                                    {/if}
                                {:else}
                                    <span class="tooltip" data-tip="{bid.pubkey}">{bid.pubkey.substring(0,6) + '...'}</span>
                                {/if}
                            </div>
                        </div>
                    </th>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
{/if}

<input type="checkbox" id="skin_in_the_game_modal" class="modal-toggle" />
<div class="modal">
    <div class="modal-box">
        <h3 class="font-bold text-lg">Skin in the Game proof needed!</h3>
        <p class="py-4 text-base">Bidding for this auction has reached a threshold, and participants are required to complete a <b>"Skin In The Game"</b> test as an <b>anti-spam</b> measure.</p>
        <p class="py-4 text-base">You have to buy the Plebeian Market <b>"Skin In The Game"</b> badge which costs $20. This has to be done <b>just once</b>, and you'll be able to bid on as many auctions as you want.</p>
        <p class="py-6 text-base">As soon as you have the <b>"Skin In The Game"</b> badge, <b>your bid will be approved</b>.</p>
        <div class="modal-action">
            <label for="skin_in_the_game_modal" class="btn">Close</label>
        </div>
    </div>
</div>
