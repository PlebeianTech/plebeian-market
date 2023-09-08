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
    import {encodeNpub, filterTags} from "$sharedLib/nostr/utils";
    import BadgeModal from "$lib/components/nostr/BadgeModal.svelte";
    import Twitter from "$sharedLib/components/icons/Twitter.svelte";
    import Telegram from "$sharedLib/components/icons/Telegram.svelte";
    import Github from "$sharedLib/components/icons/Github.svelte";

    /** @type {import('./$types').PageData} */
    export let data;

    $: profile = null;

    $: badgesAwarded = [];
    $: badgesAccepted = [];
    $: badgeDefinitions = new Map<string, object>();
    $: currentBadge = null;

    $: profileBadgesLastEvent = null;

    $: externalIdentities = [];

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

    function verifyExternalIdentity(channel: string, identity: string, proof: string) {
        switch (channel) {
            case "github":
                console.log("Github", identity, proof);
                let testUrl = 'https://gist.github.com/' + identity + '/' + proof;

                fetch(testUrl)
                    //.then((response) => response.json())
                    //.then((json) => console.log(json));
                    .then((response) => console.log('response', response));
                return '';
            default:
                return '';
        }
    }

    function getExternalIdentityUrl(channel: string, identity: string, proof: string) {
        switch (channel) {
            case 'github':
                return 'https://gist.github.com/' + identity + '/' + proof;
            case 'twitter':
                return 'https://twitter.com/' + identity + '/status/' + proof;
            case 'telegram':
                return 'https://t.me/' + proof;
            case 'mastodon':
                return 'https://' + identity + '/' + proof;
            default:
                return '';
        }
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
                });

            getProfileBadges(data.pubkey, (profileBadgeEvent) => {
                console.log('profileBadgeEvent',profileBadgeEvent);
                if (profileBadgesLastEvent === null || profileBadgesLastEvent.created_at < profileBadgeEvent.created_at) {
                    getBadgeDefinition(profileBadgeEvent, true);
                    profileBadgesLastEvent = profileBadgeEvent;
                }
            });

            getBadgeAward(data.pubkey, (badgeAwardEvent) => {
                console.log('badgeAwardEvent',badgeAwardEvent);
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

        <div class="mt-2 text-xl">
            <p class="mb-1 font-bold">{profile.display_name ?? profile.name ?? nip19.npubEncode(profile.pubkey)}</p>

            {#if profile.about}
                <p>{profile.about}</p>
            {/if}
            {#if profile.lud16}
                <p><a class="hover:underline tooltip tooltip-bottom" data-tip="Tip with Lightning" href="lightning:{profile.lud16}">⚡ Tips</a></p>
            {/if}
        </div>
    </div>
{/if}

{#if externalIdentities.length}
    <div class="mt-1 pb-4 md:pb-6">
        <p class="text-md mb-1 font-bold">External Identities</p>

        {#each externalIdentities as identity}
            <div class="mt-2 mb-3">
                <a class="flex hover:underline" target="_blank" href="{getExternalIdentityUrl(identity.split(':')[0], identity.split(':')[1], identity.split(':')[2])}">
                    {#if identity.split(':')[0] === 'twitter'}
                        <Twitter />
                    {:else if identity.split(':')[0] === 'github'}
                        <Github />
                    {:else if identity.split(':')[0] === 'telegram'}
                        <Telegram />
                    {/if}

                    <div class="ml-2">{identity.split(':')[1]}</div>
                </a>
            </div>
        {/each}

        <p class="text-xs leading-4">
            You can check that this identities match the external ones by clicking on each link and searching for <span class="hidden md:contents">{encodeNpub(data.pubkey)}</span><span class="flex md:hidden">{splitString(encodeNpub(data.pubkey), 32) }</span>
        </p>
    </div>
{/if}

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
                {#if !badgesAccepted.includes(badgeId) && badgeDefinitions.get(badgeId)}
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
{/if}

<StallsBrowser merchantPubkey={data.pubkey} />

<BadgeModal badgeInfo={currentBadge ? badgeDefinitions.get(currentBadge) : null} {profileBadgesLastEvent} {onImgError}  />

<!--
<ResumeView pubkey={data.pubkey} />
-->
