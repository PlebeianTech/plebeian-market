<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import { onMount } from "svelte";
    import { getFeatured } from "$lib/services/api";
    import { user, loginModalState } from "$lib/stores";
    import { type Auction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { type Listing, fromJson as listingFromJson } from "$lib/types/listing";
    import ItemCardSmall from "$lib/components/ItemCardSmall.svelte";
    import Typewriter from "$lib/components/Typewriter.svelte";
    import { page } from "$app/stores";
    import { MetaTags } from "svelte-meta-tags";

    let auctions: Auction[] | null = null;
    let listings: Listing[] | null = null;

    function go() {
        if ($user && $user.nym) {
            goToStall()
        } else {
            loginModalState.set({
                openRequested: true,
                callbackFunc: goToStall
            });
        }
    }

    function goToStall() {
        if ($user && $user.nym) {
            window.location.href = `${window.location.protocol}//${window.location.host}/stall/${$user.nym}`;
        }
    }

    onMount(async () => {
        getFeatured({endpoint: 'auctions', responseField: 'auctions', fromJson: auctionFromJson},
            a => { auctions = a; });
        getFeatured({endpoint: 'listings', responseField: 'listings', fromJson: listingFromJson},
            a => { listings = a; });
    });
</script>

<MetaTags
        title="Plebeian Market"
        description="Plebeian Market is a distributed self sovereign P2P market place."
        openGraph={{
            site_name: "Plebeian Market",
            type: "website",
            url: $page.url.href,
            title: "Plebeian Market",
            description: "Plebeian Market is a distributed self sovereign P2P market place.",
            images: [
              {
                url: "/images/Plebeian_Logo_OpenGraph.png",
                alt: "Plebeian Market logo"
              }
            ],
        }}
        twitter={{
            site: import.meta.env.VITE_TWITTER_USER,
            handle: import.meta.env.VITE_TWITTER_USER,
            cardType: "summary_large_image",
            imageAlt: "Plebeian Market logo",
        }}
/>

<div id="bgHero" class="bg-fixed">
  <div class="bg-black/80">
    <div class="grid place-items-center lg:w-2/3 mx-auto h-screen">
      <div class="grid mt-20">
        <!-- COL -->
        <div class="bg-zinc-800/40 rounded-xl shadow-xl backdrop-blur-md p-4 border border-gray-700/40">

          <div class="flex flex-col items-start">
            <Typewriter />
          </div>
          <h2 class="text-xl mt-8 uppercase text-center text-white">Get the market started</h2>
          <div class="my-8 w-full btn btn-primary p-4 border rounded flex items-center" on:click={go} on:keypress={go}>
            Let's go
           </div>
        </div>

        <!-- COL -->
      </div>
    </div>
  </div>

</div>

<div class="lg:w-2/3 mx-auto w-full lg:columns-3 space-y-2 py-20 my-20">
    {#if auctions !== null}
        {#each auctions as auction}
            <div class="h-auto my-3 self-center">
                <ItemCardSmall entity={auction} showCampaign={true} showOwner={true} />
            </div>
        {/each}
    {/if}
    {#if listings !== null}
        {#each listings as listing}
            <div class="h-auto my-3 self-center">
                <ItemCardSmall entity={listing} showCampaign={true} showOwner={true} />
            </div>
        {/each}
    {/if}
</div>

<style>
    #bgHero {
        background-image: url('$lib/images/golden-gai-tokyo.jpg');
        background-repeat: no-repeat;
        background-position: center;
        background-size: cover;
    }
</style>
