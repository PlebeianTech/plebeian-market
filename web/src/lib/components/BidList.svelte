<script lang="ts">
    import type { Auction } from "../types/auction";

    import DateFormatter from "./DateFormatter.svelte";

    export let auction: Auction;
</script>

<div class="overflow-x-auto w-full">
    <table class="table">
        <thead>
            <tr>
                <th>Bidder</th>
                <th>Amount</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            {#each auction.bids as bid}
                <tr>
                    <td>
                        <div class="flex items-center space-x-3">
                            <div class="avatar" class:verified={bid.twitter_username_verified}>
                                <div class="w-8 rounded-full">
                                    <img src={bid.twitter_profile_image_url} alt="{bid.twitter_username}'s avatar" />
                                </div>
                            </div>
                            <div>
                                <div class="font-bold">{bid.twitter_username}</div>
                                <div class="text-sm opacity-50"></div>
                            </div>
                        </div>
                    </td>
                    <td>
                        {bid.amount} sats
                    </td>
                    <td>
                        <DateFormatter date={bid.settled_at} />
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>