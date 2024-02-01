<script lang="ts">
    import {NostrPublicKey, NostrGlobalConfig, isSuperAdmin} from "$sharedLib/stores";
    import {requestLoginModal} from "$sharedLib/utils";
    import {
        setLogo,
        setFavicon,
        setWebsiteTitle
    } from "$sharedLib/pagebuilder";
    import {onMount} from "svelte";

    let logoURL = '';
    let faviconURL = '';
    let websiteTitle = '';

    onMount(async () => {
        if ($NostrGlobalConfig.content.logo) {
            logoURL = $NostrGlobalConfig.content.logo;
        }
        if ($NostrGlobalConfig.content.favicon) {
            faviconURL = $NostrGlobalConfig.content.favicon;
        }
        if ($NostrGlobalConfig.content.title) {
            websiteTitle = $NostrGlobalConfig.content.title;
        }
    });
</script>

<div class="w-full items-center justify-center text-center">
    {#if $NostrPublicKey}
        {#if $isSuperAdmin}
            <h2 class="font-bold">Logo</h2>
            <div class="2xl:w-11/12 3xl:w-9/12 mx-auto text-xs md:text-base mb-8">
                <div class="my-1">
                    <input type="text" bind:value={logoURL} placeholder="URL of logo" class="input input-bordered input-success w-full max-w-xs input-sm" />
                    <button class="btn btn-sm btn-success ml-1"
                            on:click={() => {setLogo(logoURL)}}>
                        Save
                    </button>
                </div>
            </div>

            <h2 class="font-bold">Favicon</h2>
            <div class="2xl:w-11/12 3xl:w-9/12 mx-auto text-xs md:text-base mb-8">
                <div class="my-1">
                    <input type="text" bind:value={faviconURL} placeholder="URL of favicon" class="input input-bordered input-success w-full max-w-xs input-sm" />
                    <button class="btn btn-sm btn-success ml-1"
                            on:click={() => {setFavicon(faviconURL)}}>
                        Save
                    </button>
                </div>
            </div>

            <h2 class="font-bold">Website Title</h2>
            <div class="2xl:w-11/12 3xl:w-9/12 mx-auto text-xs md:text-base mb-20">
                <div class="my-1">
                    <input type="text" bind:value={websiteTitle} placeholder="Title" class="input input-bordered input-success w-full max-w-xs input-sm" />
                    <button class="btn btn-sm btn-success ml-1"
                            on:click={() => {setWebsiteTitle(websiteTitle)}}>
                        Save
                    </button>
                </div>
            </div>
        {:else}
            <p>You need to be the owner of this website to be able to customize its default appearance.</p>
            <p class="mt-6">To claim ownership, you need to <b>edit the file <code>config.json</code></b> and put there your <b>Nostr public key</b>: {$NostrPublicKey} </p>
            <p class="mt-6">You'll then be able to come to this page and customize your installation of Plebeian Market.</p>
        {/if}
    {:else}
        <p>You need to be the owner of this website and login using your Nostr account:</p>
        <button class="btn btn-info mt-4" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
    {/if}
</div>

