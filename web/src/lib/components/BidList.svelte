<script lang="ts">
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
                        <div class="flex items-center space-x-3">
                            <Avatar account={bid.buyer} nymOnly={true} />
                            <p class="md:hidden text-xs">
                                <DateFormatter date={bid.settled_at} style={DateStyle.Short} />
                            </p>
                        </div>
                    </td>
                    <td>
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