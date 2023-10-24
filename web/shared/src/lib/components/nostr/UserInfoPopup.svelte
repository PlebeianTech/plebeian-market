<script lang="ts">
    import UserProfileInformation from "$sharedLib/components/nostr/UserProfileInformation.svelte";
    import {nip19} from "nostr-tools";
    import profilePicturePlaceHolder from "$sharedLib/images/profile_picture_placeholder.svg";
    import badgeImageFallback from "$sharedLib/images/badge_placeholder.svg";
    import ShowExternalIdentities from "$sharedLib/components/nostr/ShowExternalIdentities.svelte";
    import {Info, NostrPublicKey} from "$sharedLib/stores.js";
    import Copy from "$sharedLib/components/icons/Copy.svelte";

    export let userPubkey = null;

    $: if (window.user_information_modal) {
        if (userPubkey) {
            window.user_information_modal.showModal();
        }
    }

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

    function close() {
        window.user_information_modal.close();
        profile = null;
        userPubkey = null;
        profileFinishedLoading = false;
    }

    export function onImgError(image) {
        image.onerror = "";
        image.src = profilePicturePlaceHolder;
    }
</script>

<dialog id="user_information_modal" class="modal">
    <div class="modal-box">
        {#if !profile}
            {#if profileFinishedLoading}
                <p>This user has no nostr profile, so there is nothing to show.</p>
            {:else}
                <p>Loading user information...</p>
            {/if}
        {:else}
            {#if profile.display_name || profile.name}
                <h2>{profile.display_name ?? profile.name ?? nip19.npubEncode(profile.pubkey)?.substring(0,20)}</h2>
            {/if}

            <!-- Avatar -->
            <div class="avatar">
                <div class="w-24 h-24 lg:w-36 lg:h-36 mt-1 lg:mt-3 mx-auto rounded-full">
                    <img class="mx-auto" src="{profile.picture ?? profilePicturePlaceHolder}" on:error={(event) => onImgError(event.srcElement)} />
                </div>
            </div>

            <!-- Public key npub -->
            <div class="w-6/12 mx-auto lg:mt-1 flex">
                <p class="text-xs text-ellipsis overflow-hidden lg:mr-1 leading-6">
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

            <!-- External identities -->
            {#if profile && externalIdentities.length}
                <div class="flex items-center">
                    <div class="mt-5 mx-auto">
                        <p class="font-bold text-lg">External Identities</p>

                        <ShowExternalIdentities
                            {profileFinishedLoading}
                            {externalIdentities}
                            nostrPublicKey={$NostrPublicKey}
                            compact={true}
                        />
                    </div>
                </div>
            {/if}
        {/if}

        <!-- Badges -->
        <div class="mt-8">
            <p class="mb-2 font-bold text-lg">Plebeian Market badges</p>

            {#if pm_badges}
                <!-- Awarded and accepted -->
                {#each [...new Set([...badgesAccepted ,...badgesAwarded])] as badgeId}
                    {#if badgeDefinitions.get(badgeId)?.pm_issued}
                        <div class="tooltip tooltip-accent"
                             data-tip="{badgeDefinitions.get(badgeId).name}"
                             on:click={() => { if (document.getElementById('badgeModalImg')) { document.getElementById('badgeModalImg').style.visibility="hidden"; }; currentBadge = badgeId; window.badge_modal.showModal()}}>
                            <figure class="h-14 w-14 ml-1 mr-1 md:ml-2 md:mr-2 avatar mask mask-squircle cursor-pointer">
                                {#if badgeDefinitions.get(badgeId).thumb && (/\.(gif|jpg|jpeg|png|webp)$/i).test(badgeDefinitions.get(badgeId).thumb)}
                                    <img src={badgeDefinitions.get(badgeId).thumb} on:error={(event) => onImgError(event.srcElement)} alt="" />
                                {:else}
                                    <img src={badgeDefinitions.get(badgeId).image ?? badgeImageFallback} on:error={(event) => onImgError(event.srcElement)} alt="" />
                                {/if}
                            </figure>
                        </div>
                    {/if}
                {/each}
            {:else}
                <div class="mt-1 mb-8 text-sm">
                    <span>This user doesn't have any Plebeian Market badge yet.</span>
                </div>
            {/if}
        </div>

        <!-- Buttons -->
        <div class="modal-action flex">
            <form method="dialog" class="mx-auto">
                <a class="btn btn-info" class:btn-disabled={!profile} href="/p/{profile?.pubkey}" target="_blank">View full profile</a>
                <button class="btn btn-outline btn-error" on:click|preventDefault={close}>Close</button>
            </form>
        </div>
    </div>
</dialog>

{#if userPubkey}
    <UserProfileInformation
        userPubkey={userPubkey}
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
{/if}