<script lang="ts">
    import { page } from "$app/stores";
    import { MetaTags } from "svelte-meta-tags";
    import {getBaseUrl} from "$sharedLib/utils";
    import Sections from "$sharedLib/components/pagebuilder/Sections.svelte";
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

<Sections pageId={0} />
