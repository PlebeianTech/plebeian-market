<script lang="ts">
    import type { Auction } from "../types/auction";

    import DateFormatter from "./DateFormatter.svelte";

    export let auction: Auction;
</script>

<div class="md:hidden w-full rounded-b-lg mb-2">
    <div class="w-full bg-black/10 rounded-t-lg py-2 mb-1">
        <span class="ml-5 text-xl">Bids</span>
    </div>
        <bids class="pt-2">
            {#each auction.bids as bid}
                <div class="flex justify-between">
                        <div class="flex justify-start w-full bg-black/5 rounded-l-lg my-0.5 p-1.5 items-center space-x-2">
                            <div class="avatar" class:verified={bid.twitter_username_verified}>
                                <div class="w-8 rounded-full">
                                    <img src={bid.twitter_profile_image_url} alt="{bid.twitter_username}'s avatar" />
                                </div>
                            </div>
                            <div>
                                <div class="w-max">
                                    <p class="font-bold text-sm translate-y-2">{bid.twitter_username}</p>
                                    <span class="text-xs"><DateFormatter date={bid.settled_at} /></span>
                                </div>
                            </div>
                        </div>
                    <div class="rounded-r-lg w-4/5 bg-black/5 my-0.5 pr-2 pt-3.5">
                        <p class="text-md font-bold text-right">{bid.amount} sats</p>
                    </div>
                </div>
            {/each}
        </bids>
</div>
<div class="hidden md:block overflow-x-auto w-full">
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