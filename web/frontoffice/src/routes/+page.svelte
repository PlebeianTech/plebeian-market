<script lang="ts">
    import Typewriter from "$sharedLib/components/Typewriter.svelte";
    import { page } from "$app/stores";
    import { MetaTags } from "svelte-meta-tags";
    import {getBaseUrl} from "$lib/utils";
    import GoldenGai from "$lib/images/golden-gai-tokyo.jpg";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";

    let whiteListedStalls = [
        'hJ2ot9L3Fr2KpM8wTUT8cD',   // Atlas Shrugged's Bullion Exchange
        'GSSW3Wn5jTWHif6HJuXBuU',   // Plebtag
        'inEMKCpE9jiCwbQvUE5Wz9',   // CARLA's & THOMAS' bio beef farm
        'Chy4h7vwk4icpnUTN9QabD',   // NAVAYOGA
        'E6dcZnWZiZKai23KmZcE2f',   // ARRIFANA SURF LODGE
    ];
</script>

<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

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

<ProductCardBrowser {whiteListedStalls} />
