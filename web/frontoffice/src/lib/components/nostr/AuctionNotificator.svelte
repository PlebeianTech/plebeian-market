<script lang="ts">
    import {NostrPublicKey, privateMessages} from "$lib/stores";
    import { goto } from "$app/navigation";
    import {page} from "$app/stores";

    let auctionsToOrder;

    $: {
        auctionsToOrder = Object.entries($privateMessages.automatic)
            .filter(([, automaticMessage]) => {
                // Stall is waiting for shipping and contact details
                return automaticMessage.type === 10;
            })
            .sort((a, b) => {
                return b[1].created_at - a[1].created_at;
            });
    }
</script>

{#if $page.url.pathname !== '/auctions' && $NostrPublicKey && auctionsToOrder.length >= 0}
    <div class="alert alert-info shadow-lg lg:p-6 mt-6 lg:mt-2 {$page.url.pathname === '/' ? 'w-10/12 mx-auto mb-8' : ''}">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <div class="ml-4">
                <h3 class="font-bold">
                    {#if auctionsToOrder.length > 1}
                        You won {auctionsToOrder.length} auctions!
                    {:else}
                        You won one auction!
                    {/if}
                </h3>
                <p>
                    Now you need to <b><span class="text-secondary">provide contact and shipping information</span></b> to the merchant.
                </p>
                <button class="btn btn-success mt-4" on:click={() => goto('/auctions')}>
                    Send information
                </button>
            </div>
        </div>
    </div>
{/if}
