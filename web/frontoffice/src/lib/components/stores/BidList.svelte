<script lang="ts">
    import {formatTimestamp} from "$lib/nostr/utils";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";
    import Clock from "$sharedLib/components/icons/Clock.svelte";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";

    export let sortedBids;
    export let userProfileInfoMap;
</script>

{#if sortedBids && sortedBids.length > 0}
    {(console.log('sortedBids', sortedBids), '')}

    <div class="mt-8">
        <table class="table table-fixed w-full text-center text-base mb-2">
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
                        <td class="font-normal text-center">{bid.amount} sats</td>
                        <td class="text-center">{formatTimestamp(bid.date)}</td>
                        <td class="text-xs text-center">
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
                                {:else}
                                    Unknown response from the marketplace
                                {/if}
                            {/if}
                        </td>
                        <td class="font-normal">
                            <div class="flex items-center space-x-3">
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
