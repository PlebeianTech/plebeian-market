<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import { onMount } from "svelte";
    import { ErrorHandler, getEntities } from "$lib/services/api";
    import { type Auction, fromJson as auctionFromJson } from "$lib/types/auction";
    import { type Listing, fromJson as listingFromJson } from "$lib/types/listing";
    import ItemCardSmall from "$lib/components/ItemCardSmall.svelte";
    import Typewriter from "$lib/components/Typewriter.svelte";
    import { page } from "$app/stores";
    import { MetaTags } from "svelte-meta-tags";
    import {getBaseUrl} from "../lib/utils";
    import GoldenGai from "$lib/images/golden-gai-tokyo.jpg";

    let auctions: Auction[] | null = null;
    let listings: Listing[] | null = null;
    $: items = (<(Auction | Listing)[]>[]).concat(auctions || [], listings || []).sort((lhs, rhs) => lhs.start_date !== null && rhs.start_date !== null ? rhs.start_date.getTime() - lhs.start_date.getTime() : 0);

    onMount(async () => {
        getEntities({endpoint: 'auctions/featured', responseField: 'auctions', fromJson: auctionFromJson}, null,
            a => { auctions = <any[]>a; }, new ErrorHandler(false));
        getEntities({endpoint: 'listings/featured', responseField: 'listings', fromJson: listingFromJson}, null,
            a => { listings = <any[]>a; }, new ErrorHandler(false));
    });
</script>

<MetaTags
        title="Plebeian Market"
        description="Plebeian Market is a distributed self sovereign P2P market place."
        openGraph={{
            site_name: import.meta.env.VITE_SITE_NAME,
            type: "website",
            url: $page.url.href,
            title: "Plebeian Market",
            description: "Plebeian Market is a distributed self sovereign P2P market place.",
            images: [
              {
                url: getBaseUrl() + "images/Plebeian_Logo_OpenGraph.png",
                alt: "Plebeian Market logo"
              }
            ],
        }}
        twitter={{
            site: import.meta.env.VITE_TWITTER_USER,
            handle: import.meta.env.VITE_TWITTER_USER,
            cardType: "summary_large_image",
            image: getBaseUrl() + "images/Plebeian_Logo_OpenGraph.png",
            imageAlt: "Plebeian Market logo",
        }}
/>

<div class="bg-no-repeat bg-center bg-cover" style="background-image: url('{GoldenGai}')">
  <div class="bg-gradient-to-r from-zinc-900 to-zinc-900/40">
    <div class="grid lg:w-2/3 mx-auto py-12">
      <div class="grid lg:place-items-start place-items-center py-8 px-8">
          <div class="">
            <Typewriter />
          </div>
      </div>
    </div>
  </div>

</div>

<div class="lg:w-2/3 mx-auto w-full lg:columns-3 space-y-2 py-4">
    {#each items as item}
        <div class="h-auto my-3 self-center">
            <ItemCardSmall entity={item} showCampaign={true} showOwner={true} />
        </div>
    {/each}
</div>
