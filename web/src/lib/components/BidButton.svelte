<script lang="ts">
    import { ErrorHandler, postBid, getEntities, buyBadge, getProfile } from "$lib/services/api";
    import { BTC2USD, Info, token, user } from "$lib/stores";
    import { sats2usd } from "$lib/utils";
    import type { Auction } from "$lib/types/auction";
    import { SaleState, type Sale, fromJson as saleFromJson } from "$lib/types/sale";
    import AmountFormatter, { AmountFormat } from "$lib/components/AmountFormatter.svelte";
    import BadgeHelp from "$lib/components/BadgeHelp.svelte";
    import BadgeSVG from "$lib/components/BadgeSVG.svelte";
    import SaleFlowBadge from "$lib/components/SaleFlowBadge.svelte";
    import QR from "$lib/components/QR.svelte";

    export let amount;
    export let auction: Auction;

    let badgeSale: Sale | null = null;
    let interval: ReturnType<typeof setInterval> | undefined = undefined;

    function repostBid() {
        // repost the bid after we purchased the badge
        postBid($token, auction.key, amount, 'NEW_BADGE',
            (r, q, messages) => {
                paymentRequest = r;
                paymentQr = q;
                for (const message of messages) {
                    setTimeout(() => Info.set(message), 0);
                }
            });
    }

    function refreshBadgeSale() {
        if (badgeSale === null) {
            clearInterval(interval);
            interval = undefined;
        }

        getEntities({endpoint: "users/me/purchases", responseField: 'purchases', fromJson: saleFromJson}, $token,
            (purchases) => {
                for (const p of purchases) {
                    const purchase = <Sale>p;
                    if (badgeSale && badgeSale.address === purchase.address) {
                        if (purchase.state === SaleState.TX_DETECTED || purchase.state === SaleState.TX_CONFIRMED) {
                            getProfile($token, 'me', u => { user.set(u); });
                            // repostBid();
                            badgeSale = null;
                        }
                    }
                }
            });
    }

    $: usdAmount = $BTC2USD ? sats2usd(amount, $BTC2USD) : null;

    let paymentRequest = null;
    let paymentQr = null;

    let waitingResponse = false;
    function placeBid() {
        waitingResponse = true;
        postBid($token, auction.key, amount, undefined,
            (r, q, messages) => {
                paymentRequest = r;
                paymentQr = q;
                for (const message of messages) {
                    setTimeout(() => Info.set(message), 0);
                }
                waitingResponse = false;
            },
            (badge) => {
                buyBadge($token, badge, auction.campaign_key,
                    (s) => {
                        waitingResponse = false;
                        if (s.state === SaleState.TX_DETECTED || s.state === SaleState.TX_CONFIRMED) {
                            // repostBid();
                        } else {
                            badgeSale = s;
                            interval = setInterval(refreshBadgeSale, 1000);
                        }
                    },
                    new ErrorHandler(true, () => waitingResponse = false));
            },
            new ErrorHandler(true, () => waitingResponse = false));
    }

    export function waitingBidSettlement() {
        return paymentRequest !== null;
    }

    export function waitingBadgeSale() {
        return badgeSale !== null;
    }

    export function resetBid() {
        paymentQr = paymentRequest = amount = null;
    }

    export function bidConfirmed(r) {
        if (paymentRequest === r) {
            resetBid();
        }
    }
</script>

<div>
    {#if paymentQr}
        <QR qr={paymentQr} protocol="lightning" address={paymentRequest} />
    {:else if badgeSale}
        <SaleFlowBadge sale={badgeSale} />
    {:else}
        <div class="form-control w-full max-w-xs">
            <label class="label" for="bid-amount">
                <span class="label-text">Suggested bid</span>
            </label>
            <input bind:value={amount} type="number" name="bid-amount" id="bid-amount" class="input input-bordered w-full max-w-xs" />
            <label class="label" for="bid-amount">
                <span class="label-text"><AmountFormatter satsAmount={amount} format={AmountFormat.Usd} /></span>
                <span class="label-text">sats</span>
            </label>
        </div>
        <div class="w-full flex items-center justify-center mt-2">
            {#if waitingResponse}
                <button class="btn" disabled>Bid</button>
            {:else}
                <div class="flex gap-4 justify-center items-center">
                    <div class="my-10 glowbutton glowbutton-bid" on:click|preventDefault={placeBid} on:keypress={placeBid}></div>
                    {#if auction.campaign_key}
                        {#each auction.bid_thresholds as threshold}
                            {#if usdAmount}
                                {#if !($user && $user.hasBadge(threshold.required_badge))}
                                    {#if usdAmount > threshold.bid_amount_usd / 2}
                                        <div class="radial-progress" class:text-info={usdAmount < threshold.bid_amount_usd * 0.75} class:text-warning={usdAmount >= threshold.bid_amount_usd * 0.75 && usdAmount < threshold.bid_amount_usd * 0.85} class:text-error={usdAmount >= threshold.bid_amount_usd * 0.85} style="--value:{usdAmount / threshold.bid_amount_usd * 100};">
                                            <div class="tooltip" data-tip="Skin in the game required / click for info">
                                                <label class="cursor-help" for="badge-modal">
                                                    ${threshold.bid_amount_usd}
                                                </label>
                                            </div>
                                        </div>
                                    {/if}
                                {/if}
                            {/if}
                        {/each}
                    {/if}
                </div>
            {/if}
        </div>
    {/if}
</div>

<input type="checkbox" id="badge-modal" class="modal-toggle" />
<div class="modal">
    <div class="modal-box">
        <BadgeHelp campaign_name={auction.campaign_name} />
        <div class="modal-action">
            <label for="badge-modal" class="btn">OK</label>
        </div>
    </div>
</div>