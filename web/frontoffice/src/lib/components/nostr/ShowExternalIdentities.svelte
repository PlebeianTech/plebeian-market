<script lang="ts">
    import {askAPIForVerification, encodeNpub, getExternalIdentityUrl} from "$sharedLib/nostr/utils";
    import {NostrPublicKey} from "$sharedLib/stores";

    import Clock from "$sharedLib/components/icons/Clock.svelte";
    import VerificationMark from "$sharedLib/components/icons/VerificationMark.svelte";
    import X from "$sharedLib/components/icons/X.svelte";
    import Telegram from "$sharedLib/components/icons/Telegram.svelte";
    import Github from "$sharedLib/components/icons/Github.svelte";
    import Twitter from "$sharedLib/components/icons/Twitter.svelte";
    import {onMount} from "svelte";
    import {getConfigurationFromFile} from "$sharedLib/utils";

    export let externalIdentities;
    export let externalIdentitiesVerification;
    export let showDeleteButton = false;
    export let nostrPublicKey;

    export const verifyIdentities = callAPIVerifyIdentities;

    const identityTypesSupported = ['twitter', 'github', 'telegram'];
    $: backend_present = true;
    $: verificationCanBeDone = true;

    async function callAPIVerifyIdentities() {
        if (backend_present) {
            if (externalIdentities.length === 0) {
                return;
            }

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
        let config = await getConfigurationFromFile();
        if (config) {
            backend_present = config.backend_present ?? true;
        }
    });
</script>

{#each externalIdentities as identity}
    <div class="flex mt-5">
        {#if showDeleteButton}
            <div class="w-5 h-5 mr-4 tooltip tooltip-error" data-tip="Delete this identity from your Nostr Profile" on:click={() => {deleteIdentity(identity)}}><X /></div>
        {/if}

        <a class="flex hover:underline" target="_blank" href="{getExternalIdentityUrl(identity.split(':')[0], identity.split(':')[1], identity.split(':')[2])}">
            {#if identity.split(':')[0] === 'twitter'}
                <Twitter />
            {:else if identity.split(':')[0] === 'github'}
                <Github />
            {:else if identity.split(':')[0] === 'telegram'}
                <Telegram />
            {/if}

            <div class="ml-2">{identity.split(':')[1]}</div>

            {#if backend_present}
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

{#if !backend_present || !verificationCanBeDone}
    <p class="text-lg leading-4 mt-8">
        You can check that this identities match the external ones by clicking on each link and searching for <span class="hidden md:contents">{encodeNpub($NostrPublicKey)}</span><span class="flex md:hidden">{splitString(encodeNpub($NostrPublicKey), 32) }</span>
    </p>
{/if}
