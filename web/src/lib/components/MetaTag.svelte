<script lang="ts">
    import { onMount } from 'svelte';

    export let title: string = "Plebeian Market";
    export let description: string = "Self-sovereign marketplace built on Bitcoin and Lightning";
    export let image: string = "https://plebeian.market/images/logo.jpg";
    export let domain: string  = "plebeian.market";

    let defaultTitle = "Plebeian Market"
    let baseTitle: string = " | Plebeian Market"
    let url: string;

    onMount(() => {
        url = window.location.href
        // concat title if not on home page
        if (title !== defaultTitle) {
            title = title.concat(baseTitle);
        }
    });
</script>

        <title>{title}</title>
        <!-- HTML Meta Tags -->
        <meta name="description" content={description}>
        <!-- Facebook Meta Tags -->
        <meta property="og:url" content={url}>
        <meta property="og:type" content="website">
        <meta property="og:title" content={title}>
        <meta property="og:description" content={description}>
        <meta property="og:image" content={image}>
        <!-- Twitter Meta Tags -->
        <meta name="twitter:card" content="summary_large_image">
        <meta property="twitter:domain" content={domain}>
        <meta property="twitter:url" content={url}>
        <meta name="twitter:title" content={title}>
        <meta name="twitter:description" content={description}>
        <meta name="twitter:image" content={image}>
