<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import { onMount } from "svelte";
    import { getFeatured } from "$lib/services/api";
    import { user } from "$lib/stores";
    import { type Auction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { type Listing, fromJson as listingFromJson } from "$lib/types/listing";
    import ItemCardSmall from "$lib/components/ItemCardSmall.svelte";
    import Typewriter from "$lib/components/Typewriter.svelte";

    let auctions: Auction[] | null = null;
    let listings: Listing[] | null = null;

    function go() {
        if ($user && $user.nym) {
            window.location.href = `${window.location.protocol}//${window.location.host}/stall/${$user.nym}`;
        } else {
            window.location.href = `${window.location.protocol}//${window.location.host}/login`;
        }
        
    }

    onMount(async () => {
        getFeatured({endpoint: 'auctions', responseField: 'auctions', fromJson: auctionFromJson},
            a => { auctions = a; });
        getFeatured({endpoint: 'listings', responseField: 'listings', fromJson: listingFromJson},
            a => { listings = a; });
    });
</script>

<div id="bgHero" class="h-screen">
  <div class="lg:block hidden items-start lg:w-2/3 mx-auto">
    <div class="grid lg:grid-cols-2 gap-4 mt-20">
      <!-- COL -->
      <div>

        <div class="flex flex-col items-start">
          <Typewriter />
        </div>
        <h2 class="text-xl mt-8 uppercase">Get the market started</h2>
        <div class="my-8 w-full btn btn-primary p-4 border rounded flex items-center" on:click={go} on:keypress={go}>
          Let's go
         </div>
      </div>
    </div>
  </div>

</div>

<div class="grid grid-cols-1 w-full gap-4 md:grid-cols-2 lg:grid-cols-3">
    {#if auctions !== null}
        {#each auctions as auction}
            <div class="h-auto my-3 self-center glowbox">
                <ItemCardSmall entity={auction} showCampaign={true} showOwner={true} />
            </div>
        {/each}
    {/if}
    {#if listings !== null}
        {#each listings as listing}
            <div class="h-auto my-3 self-center glowbox">
                <ItemCardSmall entity={listing} showCampaign={true} showOwner={true} />
            </div>
        {/each}
    {/if}
</div>


<style>

</style>