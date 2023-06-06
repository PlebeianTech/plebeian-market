<script lang="ts">
    import { nip19 } from "nostr-tools";
    import type { Auction } from "$lib/types/auction";
    import AmountFormatter from "$lib/components/AmountFormatter.svelte";
    import Avatar from "$lib/components/Avatar.svelte";
    import DateFormatter, { DateStyle } from "$lib/components/DateFormatter.svelte";

    export let auction: Auction;
</script>

<div class="overflow-x-auto w-full md:w-auto">
    <table class="table w-full">
        <thead>
            <tr>
                <th>
                    <p class="hidden md:contents">Bidder</p>
                    <p class="md:hidden">Bids</p>
                </th>
                <th>
                    <p class="hidden md:contents">Amount</p>
                </th>
                <th>
                    <p class="hidden md:contents">Date</p>
                </th>
            </tr>
        </thead>
        <tbody>
            {#each auction.bids as bid}
                <tr>
                    <td>
                        {#if bid.buyer.nostrPublicKey && bid.buyer.nostrPublicKeyVerified}
                            <div><a class="link" target="_blank" href="https://snort.social/p/{nip19.npubEncode(bid.buyer.nostrPublicKey)}">{nip19.npubEncode(bid.buyer.nostrPublicKey)}</a></div>
                        {:else}
                            <div class="lg:flex items-center space-x-3">
                                <Avatar account={bid.buyer} />
                                <p class="md:hidden text-xs my-2">
                                    <DateFormatter date={bid.settled_at} style={DateStyle.Short} />
                                </p>
                            </div>
                        {/if}
                    </td>
                    <td class="rounded-md" class:bg-success={bid.is_winning_bid} class:text-success-content={bid.is_winning_bid}>
                        <p class="hidden md:contents">
                            <AmountFormatter satsAmount={bid.amount} newline={true} />
                        </p>
                    </td>
                    <td>
                        <p class="hidden md:contents">
                            <DateFormatter date={bid.settled_at} style={DateStyle.Short} />
                        </p>
                        <p class="md:hidden">
                            <AmountFormatter satsAmount={bid.amount} newline={true} />
                        </p>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>