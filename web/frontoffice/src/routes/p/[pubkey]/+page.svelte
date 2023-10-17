<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ResumeView from "$lib/components/resume/View.svelte";
    import StallsBrowser from "$lib/components/stores/StallsBrowser.svelte";
    import {Info, NostrPublicKey} from "$sharedLib/stores";
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
    import {decodeNpub,filterTags} from "$sharedLib/nostr/utils";
    import BadgeModal from "$lib/components/nostr/BadgeModal.svelte";
    import ShowExternalIdentities from "$lib/components/nostr/ShowExternalIdentities.svelte";
    import Copy from "$sharedLib/components/icons/Copy.svelte";

    /** @type {import('./$types').PageData} */
    export let data;

    $: profile = null;

    $: badgesAwarded = [];
    $: badgesAccepted = [];
    $: badgeDefinitions = new Map<string, object>();
    $: currentBadge = null;

    $: profileBadgesLastEvent = null;

    $: pm_badges = false;
    $: other_badges = false;

    $: externalIdentities = [];
    let externalIdentitiesVerification = {
        twitter: {verified: 'waiting'},
        github: {verified: 'waiting'},
        telegram: {verified: 'waiting'}
    }

    let verifyIdentities;

    let otherBadgesOpened = false;

    export function onImgError(image) {
        image.onerror = "";
        image.src = badgeImageFallback;
    }

    function getBadgeDefinition(badgeEvent: object, isProfileBadge: boolean) {
        filterTags(badgeEvent.tags, 'a').forEach(tagId => {
            const badgeFullName = tagId[1];
            let badgeIDarray = badgeFullName.split(':');
            let badgeName: string = badgeIDarray[2];
            let badgeAuthor: string = badgeIDarray[1];

            getBadgeDefinitions(badgeName, badgeAuthor, (badgeDefinition) => {
                // console.log('------- BadgeDefinition', badgeDefinition);

                let badgeObject = Object.fromEntries(badgeDefinition.tags);

                badgeObject.badgeFullName = badgeFullName;
                badgeObject.eventId = badgeEvent.id;        // Event ID from the "Badge Award"

                if (badgeDefinition.pubkey === '76cc29acb8008c68b105cf655d34de0b1f7bc0215eaae6bbc83173d6d3f7b987') {
                    badgeObject.pm_issued = true;
                    pm_badges = true;
                } else {
                    badgeObject.pm_issued = false;
                    other_badges = true;
                }


                if (!badgeDefinitions.get(badgeFullName)) {
                    if (isProfileBadge) {
                        badgeObject.accepted = isProfileBadge;
                    }

                    badgeDefinitions.set(badgeFullName, badgeObject);
                }

                if (isProfileBadge) {
                    if (!badgesAccepted.includes(badgeFullName)) {
                        badgesAccepted.push(badgeFullName);
                        badgesAccepted = badgesAccepted;
                    }
                } else {
                    if (!badgesAwarded.includes(badgeFullName)) {
                        badgesAwarded.push(badgeFullName);
                        badgesAwarded = badgesAwarded;
                    }
                }
            });
        });
    }

    onMount(async () => {
        if (data && data.pubkey) {
            if (data.pubkey.startsWith('npub')) {
                data.pubkey = decodeNpub(data.pubkey);
            }

            subscribeMetadata([data.pubkey],
                (pk, profileMeta) => {
                    if (profile === null || profile.created_at < profileMeta.created_at) {
                        profile = profileMeta;

                        externalIdentities = [];

                        filterTags(profile.tags, 'i').forEach(externalIdentity => {
                            const externalIdentityToken: string = externalIdentity[1] + ':' + externalIdentity[2];

                            if (!externalIdentities.includes(externalIdentityToken)) {
                                externalIdentities.push(externalIdentityToken);
                                externalIdentities = externalIdentities;
                            }
                        });
                    }
                },
                async () => {
                    await verifyIdentities();
                });

            getProfileBadges(data.pubkey, (profileBadgeEvent) => {
                if (profileBadgesLastEvent === null || profileBadgesLastEvent.created_at < profileBadgeEvent.created_at) {
                    getBadgeDefinition(profileBadgeEvent, true);
                    profileBadgesLastEvent = profileBadgeEvent;
                }
            });

            getBadgeAward(data.pubkey, (badgeAwardEvent) => {
                getBadgeDefinition(badgeAwardEvent, false);
            });
        }
    });
</script>

{#if data.pubkey === $NostrPublicKey}
    <Titleh1>Your profile</Titleh1>
{/if}


{#if profile}
    {#if data.pubkey !== $NostrPublicKey && (profile.display_name || profile.name)}
        <Titleh1>
            {profile.display_name ?? profile.name ?? nip19.npubEncode(profile.pubkey)?.substring(0,20)}
        </Titleh1>
    {/if}

    <div class="lg:flex w-full pb-4 md:pb-8">
        <!-- Desktop -->
        <div class="avatar hidden lg:block mr-8">
            <div class="w-36 h-36 mx-auto rounded-full">
                <img class="mx-auto" src="{profile.picture ?? profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} />
            </div>
        </div>
        <!-- Mobile -->
        <div class="avatar container block lg:hidden -mt-4 mb-4">
            <div class="w-36 h-36 mx-auto rounded-full">
                <img class="mx-auto" src="{profile.picture ?? profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} />
            </div>
        </div>

        <div class="mt-2">
            <div class="w-full mb-4 flex">
                <p class="font-bold text-ellipsis overflow-hidden lg:mr-2">
                    {nip19.npubEncode(profile.pubkey)}
                </p>
                <button class="btn btn-square btn-xs"
                        on:click={() => {
                            navigator.clipboard.writeText(nip19.npubEncode(profile.pubkey));
                            Info.set('Public key copied to clipboard.')
                        }}>
                    <Copy />
                </button>
            </div>
            {#if profile.about}
                <p class="mb-6 text-justify text-lg">{profile.about}</p>
            {/if}
            {#if profile.lud16}
                <p class="mb-1 text-xl"><a class="hover:underline tooltip tooltip-bottom" data-tip="Tip with Lightning" href="lightning:{profile.lud16}">⚡ Tips</a></p>
            {/if}
        </div>
    </div>
{/if}

{#if profile && externalIdentities.length}
    <div class="mt-1 pb-4 md:pb-6">
        <p class="mb-1 font-bold text-xl">External Identities</p>

        <ShowExternalIdentities
                {externalIdentities}
                {externalIdentitiesVerification}
                nostrPublicKey={profile.pubkey}
                bind:verifyIdentities={verifyIdentities}
        />
    </div>
{/if}

<div class="mt-1 pb-8 md:pb-10">
    <p class="mb-1 font-bold text-xl">Plebeian Market badges</p>

    {#if pm_badges}
        <!-- Accepted -->
        {#each badgesAccepted as badgeId}
            {#if badgeDefinitions.get(badgeId) && badgeDefinitions.get(badgeId).pm_issued}
                <div class="tooltip tooltip-accent"
                     data-tip="{badgeDefinitions.get(badgeId).name}"
                     on:click={() => { if (document.getElementById('badgeModalImg')) { document.getElementById('badgeModalImg').style.visibility="hidden"; }; currentBadge = badgeId; window.badge_modal.showModal()}}>
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
                {#if !badgesAccepted.includes(badgeId) && badgeDefinitions.get(badgeId).pm_issued && badgeDefinitions.get(badgeId)}
                    <div class="tooltip tooltip-accent"
                         data-tip="Unaccepted badge: {badgeDefinitions.get(badgeId).name}"
                         on:click={() => { if (document.getElementById('badgeModalImg')) { document.getElementById('badgeModalImg').style.visibility="hidden"; }; currentBadge = badgeId; window.badge_modal.showModal()}}>
                        <figure class="h-14 w-14 mr-2 md:mr-4 avatar mask mask-squircle cursor-pointer opacity-40 hover:opacity-80">
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
    {/if}

    <div class="mt-1 mb-8 text-lg">
        {#if data.pubkey === $NostrPublicKey}
            {#if pm_badges}
                Learn how to get more PM badges to show in your profile <a href="/faq?question=howToGetPMBadge" target="_blank" class="lg:tooltip underline" data-tip="Click to read: How do I get a Plebeian Market badge?">here</a>.
            {:else}
                You don't have Plebeian Market badges yet. Learn how to get one <a href="/faq?question=howToGetPMBadge" target="_blank" class="lg:tooltip underline" data-tip="Click to read: How do I get a Plebeian Market badge?">here</a>.
            {/if}
        {:else}
            {#if !pm_badges}
                <span>This user doesn't have any Plebeian Market badge yet.</span>
            {/if}
        {/if}
    </div>

    {#if other_badges}
        <div class="collapse bg-base-200 w-full md:w-2/5">
            <input type="checkbox" bind:checked={otherBadgesOpened} />
            <div class="collapse-title">
                <p class="text-xl font-bold">
                    <input type="checkbox" class="toggle toggle-info mr-4 left-0 text-left float-left" bind:checked={otherBadgesOpened} />
                    See other badges
                    <!-- <input type="checkbox" class="toggle toggle-info right-0 text-right float-right" bind:checked={otherBadgesOpened} /> -->
                </p>

            </div>
            <div class="collapse-content">
                <!-- Accepted -->
                {#each badgesAccepted as badgeId}
                    {#if badgeDefinitions.get(badgeId) && !badgeDefinitions.get(badgeId).pm_issued}
                        <div class="tooltip tooltip-accent"
                             data-tip="{badgeDefinitions.get(badgeId).name}"
                             on:click={() => { if (document.getElementById('badgeModalImg')) { document.getElementById('badgeModalImg').style.visibility="hidden"; }; currentBadge = badgeId; window.badge_modal.showModal()}}>
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
                        {#if !badgesAccepted.includes(badgeId) && !badgeDefinitions.get(badgeId).pm_issued && badgeDefinitions.get(badgeId)}
                            <div class="tooltip tooltip-accent"
                                 data-tip="Unaccepted badge: {badgeDefinitions.get(badgeId).name}"
                                 on:click={() => { if (document.getElementById('badgeModalImg')) { document.getElementById('badgeModalImg').style.visibility="hidden"; }; currentBadge = badgeId; window.badge_modal.showModal()}}>
                                <figure class="h-14 w-14 mr-2 md:mr-4 avatar mask mask-squircle cursor-pointer opacity-40 hover:opacity-80">
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
        </div>
    {/if}
</div>

<StallsBrowser merchantPubkey={data.pubkey} />

<BadgeModal badgeInfo={currentBadge ? badgeDefinitions.get(currentBadge) : null} {profileBadgesLastEvent} {onImgError} myBadge={data.pubkey === $NostrPublicKey}  />

<!--
<ResumeView pubkey={data.pubkey} />
-->
