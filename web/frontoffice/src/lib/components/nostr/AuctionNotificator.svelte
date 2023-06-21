<script lang="ts">
    import {NostrPublicKey} from "$lib/stores";
    import {subscribeWonAuctions} from "$lib/services/nostr";
    import { goto } from "$app/navigation";

    let auctionsIWon = [];

    export async function getNostrDMs() {
        await subscribeWonAuctions($NostrPublicKey,
            (wonAuctionEvent) => {
                let bidResponse = JSON.parse(wonAuctionEvent.content);

                console.log('wonAuctionEvent_2', bidResponse);

                if (bidResponse.status === 'winner') {
                    // TODO: check if auction details already provided

                    if (!auctionsIWon.includes(wonAuctionEvent.id)) {
                        auctionsIWon.push(wonAuctionEvent.id);
                        auctionsIWon = auctionsIWon;
                    }
                }
            },
        );
    }

    function gotoMessages() {
        goto('/messages')
    }

    $: if ($NostrPublicKey) {
        getNostrDMs();
    }
</script>

{#if $NostrPublicKey && auctionsIWon.length > 0}
    <div class="alert alert-info shadow-lg lg:p-6 mt-6 lg:mt-2">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <div class="ml-4">
                <h3 class="font-bold">
                    {#if auctionsIWon.length > 1}
                        You won {auctionsIWon.length} auctions!
                    {:else}
                        You won one auction!
                    {/if}
                </h3>
                <!-- <div class="text-xs">You have 1 unread message</div> -->
            </div>
        </div>
    </div>
{/if}
