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
    import {
        askAPIForVerification,
        decodeNpub,
        encodeNpub,
        filterTags,
        getExternalIdentityUrl
    } from "$sharedLib/nostr/utils";
    import BadgeModal from "$lib/components/nostr/BadgeModal.svelte";
    import Twitter from "$sharedLib/components/icons/Twitter.svelte";
    import Telegram from "$sharedLib/components/icons/Telegram.svelte";
    import Github from "$sharedLib/components/icons/Github.svelte";
    import Clock from "$sharedLib/components/icons/Clock.svelte";
    import VerificationMark from "$sharedLib/components/icons/VerificationMark.svelte";
    import X from "$sharedLib/components/icons/X.svelte";
    import {getConfigurationFromFile} from "$sharedLib/utils";

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

    $: backend_present = true;
    $: externalIdentities = [];
    const identityTypesSupported = ['twitter', 'github', 'telegram'];
    let externalIdentitiesVerification = {
        twitter: {verified: 'waiting'},
        github: {verified: 'waiting'},
        telegram: {verified: 'waiting'}
    }
    $: verificationCanBeDone = true;

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

    function splitString(str, length) {
        var words = str.split(" ");
        for (var j = 0; j < words.length; j++) {
            var l = words[j].length;
            if (l > length) {
                var result = [], i = 0;
                while (i < l) {
                    result.push(words[j].substr(i, length))
                    i += length;
                }
                words[j] = result.join(" ");
            }
        }
        return words.join(" ");
    }

    onMount(async () => {
        if (data && data.pubkey) {
            if (data.pubkey.startsWith('npub')) {
                data.pubkey = decodeNpub(data.pubkey);
            }

            let config = await getConfigurationFromFile();
            if (config) {
                backend_present = config.backend_present ?? true;
            }

            subscribeMetadata([data.pubkey],
                (pk, profileMeta) => {
                    if (profile === null || profile.created_at < profileMeta.created_at) {
                        profile = profileMeta;

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
                    if (backend_present) {
                        const verifiedIdentities = await askAPIForVerification(data.pubkey) ?? [];
                        console.log('askAPIForVerification - verifiedIdentities', verifiedIdentities);

                        if (!verifiedIdentities) {
                            verificationCanBeDone = false;
                        } else {
                            verifiedIdentities.forEach(verifiedIdentity => {
                                externalIdentitiesVerification[verifiedIdentity.split(':')[0]].verified = 'verified-ok';
                            });

                            identityTypesSupported.forEach(identityType => {
                                if (externalIdentitiesVerification[identityType].verified !== 'verified-ok') {
                                    externalIdentitiesVerification[identityType].verified = 'verified-notok';
                                }
                            });
                        }
                    } else {
                        verificationCanBeDone = false;
                    }
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

        <div class="mt-2">
            <p class="mb-1 font-bold text-xl">{profile.display_name ?? profile.name ?? nip19.npubEncode(profile.pubkey)}</p>

            {#if profile.about}
                <p class="text-lg">{profile.about}</p>
            {/if}
            {#if profile.lud16}
                <p><a class="hover:underline tooltip tooltip-bottom" data-tip="Tip with Lightning" href="lightning:{profile.lud16}">⚡ Tips</a></p>
            {/if}
        </div>
    </div>
{/if}

{#if externalIdentities.length}
    <div class="mt-1 pb-4 md:pb-6">
        <p class="mb-1 font-bold text-xl">External Identities</p>

        {#each externalIdentities as identity}
            {#if identityTypesSupported.includes(identity.split(':')[0])}
                <div class="mt-2 mb-3 flex text-lg">
                    {#if identity.split(':')[0] === 'twitter'}
                        <Twitter />
                    {:else if identity.split(':')[0] === 'github'}
                        <Github />
                    {:else if identity.split(':')[0] === 'telegram'}
                        <Telegram />
                    {/if}

                    <a class="hover:underline" target="_blank" href="{getExternalIdentityUrl(identity.split(':')[0], identity.split(':')[1], identity.split(':')[2])}">
                        <div class="ml-2">{identity.split(':')[1]}</div>
                    </a>

                    {#if backend_present}
                        {#if verificationCanBeDone && externalIdentitiesVerification[identity.split(':')[0]].verified === 'waiting'}
                            <div class="w-5 h-5 mt-1 ml-2 tooltip tooltip-warning text-orange-500" data-tip="Verifying identity..."><Clock /></div>
                        {:else if verificationCanBeDone && externalIdentitiesVerification[identity.split(':')[0]].verified === 'verified-ok'}
                            <div class="w-5 h-5 mt-1 ml-2 tooltip tooltip-success text-green-500" data-tip="Identity verified by Plebeian Market"><VerificationMark /></div>
                        {:else if verificationCanBeDone && externalIdentitiesVerification[identity.split(':')[0]].verified === 'verified-notok'}
                            <div class="w-5 h-5 ml-2 tooltip tooltip-error text-red-500" data-tip="This identity couldn't be verified by Plebeian Market as belonging to this user"><X /></div>
                        {/if}
                    {/if}
                </div>
            {/if}
        {/each}

        {#if !backend_present || !verificationCanBeDone}
            <p class="text-lg leading-4">
                You can check that this identities match the external ones by clicking on each link and searching for <span class="hidden md:contents">{encodeNpub(data.pubkey)}</span><span class="flex md:hidden">{splitString(encodeNpub(data.pubkey), 32) }</span>
            </p>
        {/if}
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
            <span>This user doesn't have any Plebeian Market badge yet.</span>
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

<BadgeModal badgeInfo={currentBadge ? badgeDefinitions.get(currentBadge) : null} {profileBadgesLastEvent} {onImgError}  />

<!--
<ResumeView pubkey={data.pubkey} />
-->
