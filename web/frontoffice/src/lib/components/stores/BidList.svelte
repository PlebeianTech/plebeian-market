<script lang="ts">
    import {formatTimestamp} from "$sharedLib/nostr/utils";
    import profilePicturePlaceHolder from "$sharedLib/images/profile_picture_placeholder.svg";
    import Clock from "$sharedLib/components/icons/Clock.svelte";
    import WinnerBadge from "$sharedLib/components/icons/WinnerBadge.svelte";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";
    import UserInfoPopup from "$sharedLib/components/nostr/UserInfoPopup.svelte";
    import {NostrPublicKey} from "$sharedLib/stores";
    import {nip19} from "nostr-tools";

    export let sortedBids;
    export let userProfileInfoMap;
    export let openSitgBadgeInfo;

    let openModalWithPubkey = null;
    let hoverTimer = null;

    const winnerColor = 'bg-green-300 dark:bg-[#446600]';
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
                {#if bid.amount}
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
                                                {#if bid.pubkey === $NostrPublicKey}
                                                    <p>You need to pass the "<b>Skin in the Game</b>" process before the bid is accepted.</p>
                                                    <button class="btn btn-sm btn-success" on:click|preventDefault={() => openSitgBadgeInfo(bid.backendResponse.badge_stall_id, bid.backendResponse.badge_product_id, true)}>See more details here</button>
                                                {:else}
                                                    <p>"<b>Skin in the Game</b>" process needs to be done by this user before the bid is accepted.</p>
                                                    <a class="cursor-pointer underline" on:click|preventDefault={() => openSitgBadgeInfo(bid.backendResponse.badge_stall_id, bid.backendResponse.badge_product_id, false)}>See more details here</a>.
                                                {/if}
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
                                <div class="avatar mask mask-squircle w-12 h-12" on:click={() => {openModalWithPubkey=bid.pubkey}}>
                                    <img src={userProfileInfoMap.get(bid.pubkey)?.picture ?? profilePicturePlaceHolder} alt="Avatar of the identity that made the bid" />
                                </div>
                                <div class="flex">
                                    <span class="tooltip" data-tip="{bid.pubkey}">{userProfileInfoMap.get(bid.pubkey)?.name?.substring(0,15) ?? bid.pubkey.substring(0,9) + '...'}</span>
                                    {#if userProfileInfoMap.get(bid.pubkey)?.nip05VerifiedAddress}
                                        <span class="ml-1">
                                            <Nip05Checkmark address="{userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}" />
                                        </span>
                                    {/if}
                                </div>
                            </div>
                        </th>
                    </tr>
                {/if}
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
                    <th>
                        Bidder
                        <p class="text-[10px]">(hover profile pictures with the mouse)</p>
                    </th>
                </tr>
            </thead>
            <tbody>
            {#each sortedBids as [_, bid]}
                {#if bid.amount}
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
                                            {#if bid.pubkey === $NostrPublicKey}
                                                <p class="mb-2">You need to pass the "<b>Skin in the Game</b>" process before the bid is accepted.</p>
                                                <button class="btn btn-sm btn-success" on:click|preventDefault={() => openSitgBadgeInfo(bid.backendResponse.badge_stall_id, bid.backendResponse.badge_product_id, true)}>See how to do it here</button>
                                            {:else}
                                                <p class="mb-1">"<b>Skin in the Game</b>" process needs to be done by this user before the bid is accepted.</p>
                                                <a class="cursor-pointer underline" href={null} on:click|preventDefault={() => openSitgBadgeInfo(bid.backendResponse.badge_stall_id, bid.backendResponse.badge_product_id, false)}>(more details)</a>
                                            {/if}
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
                                <div class="avatar mask mask-squircle w-12 h-12"
                                     on:mouseover={() => {hoverTimer=window.setTimeout(function(){openModalWithPubkey=bid.pubkey},500)}}
                                     on:mouseout={() => {
                                         if (hoverTimer) {
                                            window.clearTimeout(hoverTimer);
                                         }
                                         openModalWithPubkey = null;
                                     }}
                                >
                                    <img src={userProfileInfoMap.get(bid.pubkey)?.picture ?? profilePicturePlaceHolder} alt="Avatar of the identity that made the bid" />
                                </div>
                                <div class="flex">
                                    <a href="/p/{nip19.npubEncode(bid.pubkey)}"
                                       target="_blank"
                                       class="tooltip underline"
                                       data-tip="{bid.pubkey}">
                                        {userProfileInfoMap.get(bid.pubkey)?.name?.substring(0,30) ?? bid.pubkey.substring(0,12) + '...'}
                                    </a>
                                    {#if userProfileInfoMap.get(bid.pubkey)?.nip05VerifiedAddress}
                                        <span class="mt-1 ml-2">
                                            <Nip05Checkmark address="{userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}" />
                                        </span>
                                    {/if}
                                </div>
                            </div>
                        </th>
                    </tr>
                {/if}
            {/each}
            </tbody>
        </table>
    </div>
{/if}

<UserInfoPopup bind:userPubkey={openModalWithPubkey} />
