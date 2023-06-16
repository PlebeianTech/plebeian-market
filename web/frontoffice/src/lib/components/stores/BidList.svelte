<script lang="ts">
    import {formatTimestamp} from "$lib/nostr/utils";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";
    import Clock from "$sharedLib/components/icons/Clock.svelte";

    export let sortedBids;
</script>

{#if sortedBids && sortedBids.length > 0}
    {(console.log('sortedBids', sortedBids), '')}

    <div class="mt-8">
        <table class="table border w-full text-center text-base">
            <!-- head -->
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
                        <th class="font-normal">{bid.amount} sats</th>
                        <td>{formatTimestamp(bid.date)}</td>
                        <td class="text-xs text-center">
                            {#if !bid.backendResponse && i!==1}
                                <div class="w-8 h-8 mx-auto"><Clock /></div>
                                Waiting response from backend
                            {:else}
                                {#if bid.backendResponse === '+' || i===1}
                                    <div class="text-xl mx-auto tooltip" data-tip="Bid confirmed">✅</div>
                                {:else}
                                    Unknown response from the backend
                                {/if}
                            {/if}
                        </td>
                        <th class="font-normal">
                            <div class="flex items-center space-x-3">
                                <div class="avatar">
                                    <div class="mask mask-squircle w-12 h-12">
                                        <img src={bid.profile?.image ?? profilePicturePlaceHolder} alt="Avatar Tailwind CSS Component" />
                                    </div>
                                </div>
                                <div>
                                    {#if bid.profile}
                                        {bid.profile.name ?? ''}
                                        <!--<div class="text-sm opacity-50">United States</div> -->
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
    </div>
{/if}
