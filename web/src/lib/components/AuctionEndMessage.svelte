<script lang="ts">
    import type { Auction } from "../types/auction";
    import { user } from "../stores";
    import AmountFormatter from "./AmountFormatter.svelte";
    import Handshake from "./Handshake.svelte";
    import QR from "./QR.svelte";

    export let auction: Auction;

    $: remainingPercent = auction && auction.contribution_percent ? 100 - auction.contribution_percent : null;

    $: myBidCount = auction ? auction.bids.filter(b => b.payment_request).length : 0;
    $: myContribution = myBidCount * 21; // LIGHTNING_INVOICE_AMOUNT in config.py
</script>

{#if auction.has_winner && auction.winner}
    {#if auction.is_mine}
        {#if $user && $user.nym && $user.profileImageUrl && auction.winner.nym && auction.winner.profileImageUrl}
            <div class="my-4">
                <Handshake
                    leftNym={$user.nym}
                    leftProfileImageUrl={$user.profileImageUrl}
                    rightNym={auction.winner.nym}
                    rightProfileImageUrl={auction.winner.profileImageUrl} />
            </div>
        {/if}
        <div class="my-4 text-center">
            <span class=text-3xl>Congratulations...</span> the winning bidder is
            <a class="link" href="/stall/@{auction.winner.nym}">{auction.winner.nym}</a>
        </div>
        <p class="my-2 text-center">Please contact them for the final payment of <AmountFormatter satsAmount={auction.remaining_amount} />.</p>
        {#if auction.contribution_amount}
            <p class="my-2 text-center">And thank you for your donation of <AmountFormatter satsAmount={auction.contribution_amount} />!</p>
        {/if}
    {:else if auction.is_lost}
        <p class="my-4">Unfortunately, you were outbid.</p>
        <p class="my-2">Thank you so much for taking part and contributing {#if myContribution !== 0}{myContribution} sats {/if}to open source projects on Bitcoin!</p>
    {:else if auction.is_won}
        {#if $user && $user.nym && $user.profileImageUrl && auction.seller.nym && auction.seller.profileImageUrl}
            <div class="my-4">
                <Handshake
                    leftNym={$user.nym}
                    leftProfileImageUrl={$user.profileImageUrl}
                    rightNym={auction.seller.nym}
                    rightProfileImageUrl={auction.seller.profileImageUrl} />
            </div>
        {/if}
        <p class="my-4 text-center">Thank you for your contribution! Please contact the seller directly to arrange payment of the remaining <AmountFormatter satsAmount={auction.remaining_amount} /> and delivery.</p>
    {:else}
        <p class="my-4">Congratulations to {auction.winner.nym}!</p>
        {#if auction.contribution_amount}
            <p class="my-2">The seller {auction.seller.nym} has donated <AmountFormatter satsAmount={auction.contribution_amount} /> to Bitcoin open source projects like this.
        {/if}
    {/if}
{:else if $user && auction.needs_contribution}
    <div class="my-4 text-2xl">
        <span class=text-3xl>Congratulations</span> {$user.nym}, You've won &#x1F389; &#x1F64C; &#x1F44F;
    </div>
    <p class="my-2">
        The seller wishes to donate {auction.contribution_percent}% = <AmountFormatter satsAmount={auction.contribution_amount} /> sats out of your winning bid to Plebeian Technology. Please send the amount using the QR code below!
    </p>
    <p class="my-2">
        {auction.seller.nym} is waiting for you to send us their contribution!
    </p>
    <p class="my-2">
        After payment you will be directed to the seller for final settlement of the remaining {remainingPercent}% = <AmountFormatter satsAmount={auction.remaining_amount} />.
    </p>
    <QR qr={auction.contribution_qr} protocol="lightning" address={auction.contribution_payment_request} />
{:else if $user && auction.wait_contribution}
    <p class="my-2 text-center">We are waiting for the winner to send your contribution to Plebeian Technology.</p>
{/if}