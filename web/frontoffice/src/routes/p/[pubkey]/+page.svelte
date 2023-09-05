<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ResumeView from "$lib/components/resume/View.svelte";
    import StallsBrowser from "$lib/components/stores/StallsBrowser.svelte";
    import {NostrPublicKey} from "$sharedLib/stores";
    import {
        getBadgeAward,
        getBadgeDefinitions,
        getProfileBadges,
        subscribeMetadata
    } from "$sharedLib/services/nostr";
    import profilePicturePlaceHolder from "$sharedLib/images/profile_picture_placeholder.svg";
    import badgeImageFallback from "$sharedLib/images/badge_placeholder.svg";
    import {onMount} from "svelte";
    import {nip19} from "nostr-tools";
    import {filterTags} from "$sharedLib/nostr/utils";
    import BadgeModal from "$lib/components/nostr/BadgeModal.svelte";

    /** @type {import('./$types').PageData} */
    export let data;

    $: profile = null;

    $: badgesDefinition = new Map<string, object>();
    $: badgesAccepted = [];
    $: currentBadge = null;

    export function onImgError(image) {
        image.onerror = "";
        image.src = badgeImageFallback;
    }

    onMount(async () => {
        if (data && data.pubkey) {
            subscribeMetadata([data.pubkey],
                (pk, profileMeta) => {
                    if (profile === null || profile.created_at < profileMeta.created_at) {
                        profile = profileMeta;
                    }
                });

            getProfileBadges(data.pubkey, (profileBadge) => {
                // console.log('------- ProfileBadge', profileBadge);

                filterTags(profileBadge.tags, 'a').forEach(tagId => {
                    let bedgeIDarray = tagId[1].split(':');

                    getBadgeDefinitions(bedgeIDarray[2], bedgeIDarray[1], (badgeDefinition) => {
                        // console.log('------- BadgeDefinition', badgeDefinition);

                        badgesDefinition.set(bedgeIDarray[2], Object.fromEntries(badgeDefinition.tags));

                        if (!badgesAccepted.includes(bedgeIDarray[2])) {
                            badgesAccepted.push(bedgeIDarray[2]);
                            badgesAccepted = badgesAccepted;
                        }
                    });
                });
            });

            getBadgeAward(data.pubkey, (badgeAward) => {
                // console.log('------- BadgeAward', badgeAward);
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
    <div class="flex pb-4 leading-none relative">
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

    {#if badgesAccepted.length}
        <div class="mt-1 mb-6">
            {#if data.pubkey === $NostrPublicKey}
                <p class="text-md mb-1">Your Badges</p>
            {:else}
                <p class="text-md mb-1">Badges</p>
            {/if}

            {#each badgesAccepted as badgeId}
                {#if badgesDefinition.get(badgeId)}
                    <div class="tooltip tooltip-accent" data-tip="{badgesDefinition.get(badgeId).name}" on:click={() => {currentBadge = badgeId; window.badge_modal.showModal()}}>
                        <figure class="h-14 w-14 mr-2 md:mr-4 avatar mask mask-squircle cursor-pointer">
                            {#if badgesDefinition.get(badgeId).thumb && (/\.(gif|jpg|jpeg|png|webp)$/i).test(badgesDefinition.get(badgeId).thumb)}
                                <img src={badgesDefinition.get(badgeId).thumb} on:error={(event) => onImgError(event.srcElement)} alt="" />
                            {:else}
                                <img src={badgesDefinition.get(badgeId).image ?? badgeImageFallback} on:error={(event) => onImgError(event.srcElement)} alt="" />
                            {/if}
                        </figure>
                    </div>
                {/if}
            {/each}
        </div>
    {/if}
{/if}

<StallsBrowser merchantPubkey={data.pubkey} />

<BadgeModal badgeInfo={currentBadge ? badgesDefinition.get(currentBadge) : null} {onImgError}  />

<!--
<ResumeView pubkey={data.pubkey} />
-->
