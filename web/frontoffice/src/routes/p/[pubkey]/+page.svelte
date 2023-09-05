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

    $: badgesAwarded = [];
    $: badgesAccepted = [];
    $: badgeDefinitions = new Map<string, object>();
    $: currentBadge = null;

    export function onImgError(image) {
        image.onerror = "";
        image.src = badgeImageFallback;
    }

    function getBadgeDefinition(badge: object, isProfileBadge: boolean) {
        filterTags(badge.tags, 'a').forEach(tagId => {
            let badgeIDarray = tagId[1].split(':');
            let badgeName: string = badgeIDarray[2];
            let badgeAuthor: string = badgeIDarray[1];

            getBadgeDefinitions(badgeName, badgeAuthor, (badgeDefinition) => {
                // console.log('------- BadgeDefinition', badgeDefinition);

                badgeDefinitions.set(badgeName, Object.fromEntries(badgeDefinition.tags));

                if (isProfileBadge) {
                    if (!badgesAccepted.includes(badgeName)) {
                        badgesAccepted.push(badgeName);
                        badgesAccepted = badgesAccepted;
                    }
                } else {
                    if (!badgesAwarded.includes(badgeName)) {
                        badgesAwarded.push(badgeName);
                        badgesAwarded = badgesAwarded;
                    }
                }
            });
        });
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
                // console.log('------- getProfileBadges', profileBadge);
                getBadgeDefinition(profileBadge, true);
            });

            getBadgeAward(data.pubkey, (badgeAward) => {
                // console.log('------- getBadgeAward', badgeAward);
                getBadgeDefinition(badgeAward, false);
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
    <div class="flex pb-4 md:pb-8 leading-none relative">
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

    {#if badgesAccepted.length || (data.pubkey === $NostrPublicKey && badgesAwarded.length)}
        <div class="mt-1 pb-8 md:pb-10">
            {#if data.pubkey === $NostrPublicKey}
                <p class="text-md mb-1 font-bold">Your Badges</p>
            {:else}
                <p class="text-md mb-1 font-bold">Badges</p>
            {/if}

            <!-- Accepted -->
            {#each badgesAccepted as badgeId}
                {#if badgeDefinitions.get(badgeId)}
                    <div class="tooltip tooltip-accent" data-tip="{badgeDefinitions.get(badgeId).name}" on:click={() => { if (document.getElementById('badgeModalImg')) { document.getElementById('badgeModalImg').style.visibility="hidden"; }; currentBadge = badgeId; window.badge_modal.showModal()}}>
                        <figure class="h-14 w-14 mr-2 md:mr-4 avatar mask mask-squircle cursor-pointer">
                            {#if badgeDefinitions.get(badgeId).thumb && (/\.(gif|jpg|jpeg|png|webp)$/i).test(badgeDefinitions.get(badgeId).thumb)}
                                <img src={badgeDefinitions.get(badgeId).thumb} on:error={(event) => onImgError(event.srcElement)} alt="" />
                            {:else}
                                <img src={badgeDefinitions.get(badgeId).image ?? badgeImageFallback} on:error={(event) => onImgError(event.srcElement)} alt="" />
                            {/if}
                        </figure>
                    </div>
                {/if}
            {/each}

            <!-- Awarded -->
            {#if data.pubkey === $NostrPublicKey}
                {#each badgesAwarded as badgeId}
                    {#if !badgesAccepted.includes(badgeId) && badgeDefinitions.get(badgeId)}
                        <div class="tooltip tooltip-accent" data-tip="Unaccepted badge: {badgeDefinitions.get(badgeId).name}" on:click={() => { if (document.getElementById('badgeModalImg')) { document.getElementById('badgeModalImg').style.visibility="hidden"; }; currentBadge = badgeId; window.badge_modal.showModal()}}>
                            <figure class="h-14 w-14 mr-2 md:mr-4 avatar mask mask-squircle cursor-pointer opacity-20 hover:opacity-80">
                                {#if badgeDefinitions.get(badgeId).thumb && (/\.(gif|jpg|jpeg|png|webp)$/i).test(badgeDefinitions.get(badgeId).thumb)}
                                    <img src={badgeDefinitions.get(badgeId).thumb} on:error={(event) => onImgError(event.srcElement)} alt="" />
                                {:else}
                                    <img src={badgeDefinitions.get(badgeId).image ?? badgeImageFallback} on:error={(event) => onImgError(event.srcElement)} alt="" />
                                {/if}
                            </figure>
                        </div>
                    {/if}
                {/each}
            {/if}
        </div>
    {/if}
{/if}

<StallsBrowser merchantPubkey={data.pubkey} />

<BadgeModal badgeInfo={currentBadge ? badgeDefinitions.get(currentBadge) : null} {onImgError}  />

<!--
<ResumeView pubkey={data.pubkey} />
-->
