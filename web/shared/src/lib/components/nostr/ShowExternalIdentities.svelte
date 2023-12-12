<script lang="ts">
    import {askAPIForVerification, encodeNpub, getExternalIdentityUrl} from "$sharedLib/nostr/utils.js";
    import Clock from "$sharedLib/components/icons/Clock.svelte";
    import VerificationMark from "$sharedLib/components/icons/VerificationMark.svelte";
    import X from "$sharedLib/components/icons/X.svelte";
    import Telegram from "$sharedLib/components/icons/Telegram.svelte";
    import Github from "$sharedLib/components/icons/Github.svelte";
    import Twitter from "$sharedLib/components/icons/Twitter.svelte";
    import Copy from "$sharedLib/components/icons/Copy.svelte";
    import {fileConfiguration, Info} from "$sharedLib/stores.js";

    export let profileFinishedLoading = false;
    export let externalIdentities;
    export let nostrPublicKey;
    export let deleteIdentity = false;
    export let compact = false;

    $: externalIdentitiesVerification = {};

    const identityTypesSupported = ['twitter', 'github', 'telegram'];
    $: verificationCanBeDone = true;

    $: if ($fileConfiguration.backend_present && profileFinishedLoading) {
        verifyIdentities();
    }

    async function verifyIdentities() {
        if ($fileConfiguration.backend_present) {
            if (externalIdentities.length === 0) {
                return;
            }

            externalIdentitiesVerification = {
                twitter: {verified: 'waiting'},
                github: {verified: 'waiting'},
                telegram: {verified: 'waiting'}
            };

            const verifiedIdentities = await askAPIForVerification(nostrPublicKey) ?? [];
            if (!verifiedIdentities) {
                verificationCanBeDone = false;
            } else {
                verifiedIdentities.forEach(verifiedIdentity => {
                    externalIdentitiesVerification[verifiedIdentity.split(':')[0]].verified = 'verified-ok';

                    externalIdentitiesVerification[verifiedIdentity.split(':')[0]].recently_added = false;
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
    }
</script>

{#each externalIdentities as identity}
    <div class="flex mt-5" class:mt-5={!compact} class:mt-3={compact}>
        {#if deleteIdentity}
            <div class="w-5 h-5 mr-4 tooltip tooltip-error" data-tip="Delete this identity from your Nostr Profile" on:click={() => {deleteIdentity(identity)}}><X /></div>
        {/if}

        <a class="flex hover:underline" class:text-base={compact} target="_blank" href="{getExternalIdentityUrl(identity.split(':')[0], identity.split(':')[1], identity.split(':')[2])}">
            {#if identity.split(':')[0] === 'twitter'}
                <Twitter />
            {:else if identity.split(':')[0] === 'github'}
                <Github />
            {:else if identity.split(':')[0] === 'telegram'}
                <Telegram />
            {/if}

            <div class="ml-2">{identity.split(':')[1]}</div>

            {#if $fileConfiguration.backend_present && externalIdentitiesVerification[identity.split(':')[0]]}
                {#if verificationCanBeDone && externalIdentitiesVerification[identity.split(':')[0]].verified === 'waiting' && !externalIdentitiesVerification[identity.split(':')[0]].recently_added}
                    <div class="w-5 h-5 mt-1 ml-2 tooltip tooltip-warning text-orange-500" data-tip="Verifying identity..."><Clock /></div>
                {:else if verificationCanBeDone && externalIdentitiesVerification[identity.split(':')[0]].verified === 'verified-ok' && !externalIdentitiesVerification[identity.split(':')[0]].recently_added}
                    <div class="w-5 h-5 mt-1 ml-2 tooltip tooltip-success text-green-500" data-tip="Identity verified by Plebeian Market"><VerificationMark /></div>
                {:else if verificationCanBeDone && externalIdentitiesVerification[identity.split(':')[0]].verified === 'verified-notok' && !externalIdentitiesVerification[identity.split(':')[0]].recently_added}
                    <div class="w-5 h-5 ml-2 tooltip tooltip-error text-red-500" data-tip="This identity couldn't be verified by Plebeian Market as belonging to this user"><X /></div>
                {/if}
            {/if}
        </a>
    </div>
{/each}

{#if !compact && (!$fileConfiguration.backend_present || !verificationCanBeDone)}
    <div class="flex mt-6 mb-4 w-11/12 lg:w-8/12" class:text-lg={!compact} class:text-xs={compact}>
        <p class="text-ellipsis overflow-hidden mx-auto">
            {#if !compact}
                You can check that this identities match the external ones by clicking on each link and searching for {encodeNpub(nostrPublicKey)}
            {:else}
                Check that this identities match the external ones by clicking on each link and searching for the npub of the user.
            {/if}

            <button class="btn btn-square btn-xs ml-1 mt-2"
                    on:click={() => {
                    navigator.clipboard.writeText(encodeNpub(nostrPublicKey));
                    Info.set('Public key copied to clipboard.')
                }}>
                <Copy />
            </button>
        </p>
    </div>
{/if}
