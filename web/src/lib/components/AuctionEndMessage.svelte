<script lang="ts">
    import type { Auction } from "../types/auction";
    import { user } from "../stores";
    import Handshake from "./Handshake.svelte";
    import QR from "./QR.svelte";

    export let auction: Auction;

    $: remainingPercent = auction && auction.contribution_percent ? 100 - auction.contribution_percent : null;
</script>

{#if auction.has_winner}
    {#if auction.is_mine}
        {#if auction.seller_twitter_username && auction.seller_twitter_profile_image_url && auction.winner_twitter_username && auction.winner_twitter_profile_image_url}
            <div class="my-4">
                <Handshake
                    leftUsername={auction.seller_twitter_username}
                    leftProfileImageUrl={auction.seller_twitter_profile_image_url}
                    rightUsername={auction.winner_twitter_username}
                    rightProfileImageUrl={auction.winner_twitter_profile_image_url} />
            </div>
        {/if}
        <div class="my-4 text-center">
            <span class=text-3xl>Congratulations...</span> the winning bidder is
            <a href="https://twitter.com/{auction.winner_twitter_username}">@{auction.winner_twitter_username}</a>
        </div>
        <p class="my-2 text-center">Please contact them for the final payment of {auction.remaining_amount} sats.</p>
        {#if auction.contribution_amount}
            <p class="my-2 text-center">And thank you for your donation of {auction.contribution_amount} sats!</p>
        {/if}
    {:else if auction.is_lost}
        <p class="my-4">Unfortunately, you were outbid.</p>
        <p class="my-2">Thank you so much for taking part and contributing to open source projects on Bitcoin!</p>
    {:else if auction.is_won}
        {#if $user && $user.twitterUsername && $user.twitterProfileImageUrl && auction.seller_twitter_username && auction.seller_twitter_profile_image_url}
            <div class="my-4">
                <Handshake
                    leftUsername={$user.twitterUsername}
                    leftProfileImageUrl={$user.twitterProfileImageUrl}
                    rightUsername={auction.seller_twitter_username}
                    rightProfileImageUrl={auction.seller_twitter_profile_image_url} />
            </div>
        {/if}
        <p class="my-4 text-center">Thank you for your contribution! Please contact the seller directly to arrange payment of the remaining {auction.remaining_amount} sats and delivery.</p>
    {:else}
        <p class="my-4">Congratulations to @{auction.winner_twitter_username}!</p>
        {#if auction.contribution_amount}
            <p class="my-2">The seller @{auction.seller_twitter_username} has donated {auction.contribution_amount} sats to Bitcoin open source projects like this.
        {/if}
    {/if}
{:else if $user && auction.contribution_amount}
    <div class="my-4 text-2xl">
        <span class=text-3xl>Congratulations</span> @{$user.twitterUsername}, You've won &#x1F389; &#x1F64C; &#x1F44F;
    </div>
    <p class="my-2">
        The seller wishes to donate {auction.contribution_percent}% = {auction.contribution_amount} sats out of your winning bid to Plebeian Technology. Please send the amount using the QR code below!
    </p>
    <p class="my-2">
        After payment you will be directed to the seller for final settlement of the remaining {remainingPercent}% = {auction.remaining_amount} sats.
    </p>
    <QR bind:qr={auction.contribution_qr} bind:lnurl={auction.contribution_payment_request} />
{/if}