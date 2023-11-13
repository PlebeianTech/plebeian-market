<script lang="ts">
    import Typewriter from "$lib/components/Typewriter.svelte";
    import { page } from "$app/stores";
    import { MetaTags } from "svelte-meta-tags";
    import {getConfigurationFromFile} from "$sharedLib/utils";
    import {getBaseUrl} from "$sharedLib/utils";
    import GoldenGai from "$lib/images/golden-gai-tokyo.jpg";
    import ProductCardBrowser from "$lib/components/stores/ProductCardBrowser.svelte";
    import {NostrGlobalConfig} from "$sharedLib/stores";
    import {onMount} from "svelte";

    let homepage_banner = GoldenGai;

    const maxProductsLoaded: number = 20;

    onMount(async () => {
        let config = await getConfigurationFromFile();

        if (config && config.homepage_banner_image && config.homepage_banner_image.length > 0) {
            homepage_banner = config.homepage_banner_image;
        }
    });
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

<div class="bg-no-repeat bg-center bg-cover" style="background-image: url('{homepage_banner}')">
  <div class="bg-gradient-to-r from-zinc-900 to-zinc-900/40">
    <div class="grid lg:w-2/3 mx-auto py-12">
      <div class="grid lg:place-items-start place-items-center py-8 px-8">
          <Typewriter />
      </div>
    </div>
  </div>
</div>

{#if $NostrGlobalConfig.homepage_sections && $NostrGlobalConfig.homepage_sections.length > 0}
    {#each $NostrGlobalConfig.homepage_sections ?? [] as section}
        <h1>{section.title}</h1>
    {/each}
{:else}
    <ProductCardBrowser whiteListedStalls={$NostrGlobalConfig.homepage_include_stalls} {maxProductsLoaded} />
{/if}
