<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ResumeView from "$lib/components/resume/View.svelte";
    import StallsBrowser from "$lib/components/stores/StallsBrowser.svelte";
    import {NostrPublicKey} from "$sharedLib/stores";
    import {subscribeMetadata} from "$lib/services/nostr";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";
    import {onImgError} from "$lib/shopping";
    import {onMount} from "svelte";
    import {nip19} from "nostr-tools";

    /** @type {import('./$types').PageData} */
    export let data;

    $: profile = null;

    onMount(async () => {
        if (data && data.pubkey) {
            subscribeMetadata([data.pubkey],
                (pk, profileMeta) => {
                    if (profile === null || profile.created_at < profileMeta.created_at) {
                        profile = profileMeta;
                    }
                });
        }
    });
</script>

{#if data.pubkey === $NostrPublicKey}
    <Titleh1>Your profile</Titleh1>
{:else}
    <Titleh1>Profile of user</Titleh1>
{/if}

{#if profile}
    <div class="flex pb-8 leading-none relative">
        <div class="avatar indicator align-bottom">
            <div class="w-24 h-24 mr-4 rounded-full">
                <img src="{profile.picture ?? profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} />
            </div>
        </div>

        <div class="mt-4 text-xl">
            <p class="mb-1">{profile.name ?? nip19.npubEncode(profile.pubkey)}</p>

            {#if profile.about}
                <p>{profile.about}</p>
            {/if}
            {#if profile.lud16}
                <p><a class="hover:underline tooltip tooltip-bottom" data-tip="Tip with Lightning" href="lightning:{profile.lud16}">⚡ Tips</a></p>
            {/if}
        </div>
    </div>
{/if}

<StallsBrowser merchantPubkey={data.pubkey} />

<ResumeView pubkey={data.pubkey} />
