<script lang="ts">
    import type { Auction } from "../types/auction";

    import AmountFormatter from "./AmountFormatter.svelte";
    import DateFormatter from "./DateFormatter.svelte";

    export let auction: Auction;
</script>

<div class="overflow-x-auto w-full md:w-auto">
    <table class="table w-full">
        <thead>
            <tr>
                <th><p class="hidden md:contents">Bidder</p><p class="md:hidden">Bids</p></th>
                <th><p class="hidden md:contents">Amount</p></th>
                <th><p class="hidden md:contents">Date</p></th>
            </tr>
        </thead>
        <tbody>
            {#each auction.bids as bid}
                <tr>
                    <td>
                        <div class="flex items-center space-x-3">
                            <div class="avatar" class:verified={bid.twitter_username_verified} class:not-verified={!bid.twitter_username_verified}>
                                <div class="w-8 rounded-full">
                                    <img src={bid.twitter_profile_image_url} alt="{bid.twitter_username}'s avatar" />
                                </div>
                            </div>
                            <div>
                                <div><p class="font-bold">{bid.twitter_username}</p><p class="md:hidden text-xs"><DateFormatter date={bid.settled_at} /></p></div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <p class="hidden md:contents">
                            <AmountFormatter satsAmount={bid.amount} newline={true} />
                        </p>
                    </td>
                    <td>
                        <p class="hidden md:contents"><DateFormatter date={bid.settled_at} /></p>
                        <p class="md:hidden">
                            <AmountFormatter satsAmount={bid.amount} newline={true} />
                        </p>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>