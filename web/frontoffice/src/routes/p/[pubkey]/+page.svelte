<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
    import ResumeView from "$lib/components/resume/View.svelte";
    import StallsBrowser from "$lib/components/stores/StallsBrowser.svelte";
    import {Info, NostrPublicKey} from "$sharedLib/stores";
    import profilePicturePlaceHolder from "$sharedLib/images/profile_picture_placeholder.svg";
    import badgeImageFallback from "$sharedLib/images/badge_placeholder.svg";
    import {onMount} from "svelte";
    import {nip19} from "nostr-tools";
    import {decodeNpub,filterTags} from "$sharedLib/nostr/utils";
    import BadgeModal from "$lib/components/nostr/BadgeModal.svelte";
    import ShowExternalIdentities from "$sharedLib/components/nostr/ShowExternalIdentities.svelte";
    import Copy from "$sharedLib/components/icons/Copy.svelte";
    import UserProfileInformation from "$sharedLib/components/nostr/UserProfileInformation.svelte";


    /** @type {import('./$types').PageData} */
    export let data;

    $: profile = null;
    $: profileFinishedLoading = false;

    // Badges
    $: badgesAwarded = [];
    $: badgesAccepted = [];
    $: badgeDefinitions = new Map<string, object>();
    $: currentBadge = null;
    $: profileBadgesLastEvent = null;
    $: pm_badges = false;
    $: other_badges = false;

    // External identities
    $: externalIdentities = [];

    let otherBadgesOpened = false;

    export function onImgError(image) {
        image.onerror = "";
        image.src = badgeImageFallback;
    }

    onMount(async () => {
        if (data && data.pubkey) {
            if (data.pubkey.startsWith('npub')) {
                data.pubkey = decodeNpub(data.pubkey);
            }
        }
    });
</script>

{#if profile}
    {#if profile.display_name || profile.name}
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
            {profileFinishedLoading}
            {externalIdentities}
            nostrPublicKey={profile.pubkey}
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

{#if data.pubkey && !data.pubkey.startsWith('npub')}
    <StallsBrowser merchantPubkey={data.pubkey} />

    <BadgeModal badgeInfo={currentBadge ? badgeDefinitions.get(currentBadge) : null} {profileBadgesLastEvent} {onImgError} myBadge={data.pubkey === $NostrPublicKey}  />

    <UserProfileInformation
        userPubkey={data.pubkey}
        bind:profile={profile}
        bind:profileFinishedLoading={profileFinishedLoading}
        bind:badgesAwarded={badgesAwarded}
        bind:badgesAccepted={badgesAccepted}
        bind:badgeDefinitions={badgeDefinitions}
        bind:profileBadgesLastEvent={profileBadgesLastEvent}
        bind:pm_badges={pm_badges}
        bind:other_badges={other_badges}
        bind:externalIdentities={externalIdentities}
    />

    <!--
    <ResumeView pubkey={data.pubkey} />
    -->
{/if}
