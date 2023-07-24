<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script lang="ts">
    import { page } from "$app/stores";
    import { MetaTags } from "svelte-meta-tags";
    import { login, getBaseUrl } from "$lib/utils";
    import { user, token } from "$lib/stores";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";
    import Stall from "$lib/components/settings/Stall.svelte";
    import StallView from "$lib/components/StallView.svelte";
    import { requestLoginModal } from "$sharedLib/utils";

    function onLogin() {
        setTimeout(() => {token.set(localStorage.getItem("token"))}, 0);
    }
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

{#if $user}
    {#if $user.stallName !== null && $user.stallName !== ""}
        <StallView
            baseUrl="users/me"
            owner={$user} title={null}
            description={null}
            isOwnStall={true}
            showItemsCampaign={true}
            canAddItems={true}
            showActiveAuctions={true} showPastAuctions={true}
            showActiveListings={true} showPastListings={true} />
    {:else}
        <div class="flex justify-center items-center">
            <div class="w-2/3 mt-8">
                <div class="my-4">
                    <InfoBox>Please configure your stall before you start!</InfoBox>
                </div>
                <Stall />
            </div>
        </div>
    {/if}
{:else}
    <h2 class="text-4xl text-center my-8">Stall Manager</h2>
    <div class="flex justify-center items-center mt-12 gap-4">
        <a href={null} class="btn btn-primary btn-lg normal-case" on:click={async () => requestLoginModal(() => {}, onLogin)} on:keypress={async () => requestLoginModal(() => {}, onLogin)}><b>Login using Nostr</b></a>
        <a href={null} class="btn btn-primary btn-lg normal-case" on:click={() => login()} on:keypress={() => login()}><b>Login using Lightning</b></a>
    </div>
{/if}
