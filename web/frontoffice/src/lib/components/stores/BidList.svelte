<script lang="ts">
    import {formatTimestamp} from "$lib/nostr/utils";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";
    import Clock from "$sharedLib/components/icons/Clock.svelte";
    import WinnerBadge from "$sharedLib/components/icons/WinnerBadge.svelte";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";
    import {NostrPublicKey} from "$lib/stores";

    export let sortedBids;
    export let userProfileInfoMap;

    const winnerColor = 'bg-green-300 dark:bg-[#446600]';
</script>

{#if sortedBids && sortedBids.length > 0}
    <div class="mt-8 mb-6">
        <!-- Mobile -->
        <table class="md:hidden table table-fixed w-full text-center text-base">
            <thead>
                <tr>
                    <th class="pl-0">Bid</th>
                    <th class="pr-0">Info</th>
                </tr>
            </thead>
            <tbody>
            {#each sortedBids as [bid_id, bid], i}
                <tr class="bg-red-800" class:bg-success={bid.backendResponse && bid.backendResponse.status === 'winner'}>
                    <td class="text-center {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">
                        {bid.amount} sats
                        <p class="text-xs mt-1">{formatTimestamp(bid.date)}</p>

                        <div class="mt-1 text-xs">
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
                    </td>
                    <td class="text-xs text-cente {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}r">
                        <div class="flex items-center space-x-3 mt-2">
                            <div class="avatar mask mask-squircle w-12 h-12">
                                <img src={userProfileInfoMap.get(bid.pubkey)?.picture ?? profilePicturePlaceHolder} alt="Avatar of the identity that made the bid" />
                            </div>
                            <div class="flex">
                                {#if userProfileInfoMap.get(bid.pubkey)}
                                    <span class="tooltip" data-tip="{bid.pubkey}">{userProfileInfoMap.get(bid.pubkey).name}</span>
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
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>

        <!-- Desktop -->
        <table class="hidden md:block table table-fixed w-full text-center text-base">
            <thead>
                <tr>
                    <th>Bid</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Bidder</th>
                </tr>
            </thead>
            <tbody>
            {#each sortedBids as [bid_id, bid], i}
                <tr>
                    <td class="text-center {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}"><span class="p-3">{bid.amount} sats</span></td>
                    <td class="text-center {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">{formatTimestamp(bid.date)}</td>
                    <td class="text-xs text-center {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor : ''}">
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
                    <td class="{bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">
                        <div class="flex items-center space-x-3 p-3">
                            <div class="avatar mask mask-squircle w-12 h-12">
                                <img src={userProfileInfoMap.get(bid.pubkey)?.picture ?? profilePicturePlaceHolder} alt="Avatar of the identity that made the bid" />
                            </div>
                            <div class="flex">
                                {#if userProfileInfoMap.get(bid.pubkey)}
                                    <span class="tooltip" data-tip="{bid.pubkey}">{userProfileInfoMap.get(bid.pubkey).name}</span>
                                    {#if userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}
                                            <span class="mt-1 ml-2">
                                                <Nip05Checkmark address="{userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}" />
                                            </span>
                                    {/if}
                                {:else}
                                    <span class="tooltip" data-tip="{bid.pubkey}">{bid.pubkey.substring(0,6)}...</span>
                                {/if}
                            </div>
                        </div>
                    </td>
                </tr>
            {/each}
            </tbody>
        </table>
    </div>
{/if}
