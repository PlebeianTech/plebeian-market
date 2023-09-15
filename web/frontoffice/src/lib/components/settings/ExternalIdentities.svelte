<script lang="ts">
    import {loggedIn, requestLoginModal} from "$sharedLib/utils";
    import { onMount } from 'svelte';
    import {publishMetadata, subscribeMetadata} from "$sharedLib/services/nostr";
    import {askAPIForVerification, encodeNpub, filterTags, getExternalIdentityUrl} from "$sharedLib/nostr/utils";
    import {Info, Error, NostrPublicKey} from "$sharedLib/stores";
    import Telegram from "$sharedLib/components/icons/Telegram.svelte";
    import Github from "$sharedLib/components/icons/Github.svelte";
    import Twitter from "$sharedLib/components/icons/Twitter.svelte";
    import Question from "$sharedLib/components/icons/Question.svelte";

    $: profile = null;
    $: externalIdentities = [];
    let changesMade = false;
    let lastProfileLoaded = false;

    let type = 'twitter';
    let url = '';
    let user = '';

    let verifyHelpInfo: [] = []
    verifyHelpInfo['twitter'] = {
        title: 'How to verify your Twitter / X account',
        description:
            '<ol class="list-decimal list-inside mt-4">' +
                '<li class="mb-2"><b>Create a Tweet</b> containing your npub <b><a class="underline" target="_blank"' +
                    'href="https://twitter.com/intent/tweet?text=Verifying%20that%20I%20control%20the%20following%20Nostr%20public%20key:%20' + encodeNpub($NostrPublicKey) + '">(click here)</a></b>.' +
                '</li>' +
                '<li class="mb-2">Once published, <b>open the published Tweet</b>.</li>' +
                '<li class="mb-2"><b>Copy the URL</b> and paste it in this screen.</li>' +
                '<li class="mb-2"><b>Click Add</b> to add the new identity to your Nostr profile and verify it.' +
            '</ol>' +
            '<p class="mt-6 mb-1 font-bold">Example of the URL you\'ll get:</p>' +
            '<p class="mt-1">https://twitter.com/halfin/status/1110302988</p>'
    };
    verifyHelpInfo['github'] = {
        title: 'How to verify your GitHub account',
        description:
            '<ol class="list-decimal list-inside mt-4">' +
                '<li class="mb-2"><b>Login</b> to your GitHub account</li>' +
                '<li class="mb-2"><b>Copy your npub</b> here: <span class="text-xs">' + encodeNpub($NostrPublicKey) + '</span></li>' +
                '<li class="mb-2">Go to the gists page <b><a class="underline" target="_blank"\' +\n' +
                    'href="https://gist.github.com/">(click here)</a></b>.' +
                '<li class="mb-2"><b>Paste the npub</b> into the textare in the middle.</li>' +
                '<li class="mb-2">Click the arrow on the right side of the green button and select <b>Create public gist</b>, then click the Create public gist green button.' +
                '<li class="mb-2"><b>Copy the URL</b> and paste it in this screen.</li>' +
                '<li class="mb-2"><b>Click Add</b> to add the new identity to your Nostr profile and verify it.' +
            '</ol>' +
            '<p class="mt-6 mb-1 font-bold">Example of the URL you\'ll get:</p>' +
            '<p class="mt-1">https://gist.github.com/your_username/a3158dcaf61a1c49485zf1c2719469af</p>'
    };
    verifyHelpInfo['telegram'] = {
        title: 'How to verify your Telegram account',
        description:
            '<p class="mt-4">To verify your Telegram account, you need to be able to write a message to a <i>public</i> Telegram room. We suggest using the ' +
                '<b><a class="underline" target="_blank" href="https://web.telegram.org/k/#@nostr_protocol">Nostr</a></b> or the ' +
                '<b><a class="underline" target="_blank" href="https://web.telegram.org/k/#@PlebeianMarket">Plebeian Market</a></b> channels.</p>' +
            '<ol class="mt-6 list-decimal list-inside">' +
                '<li class="mb-2">Introduce the <b>Telegram username</b> into the first field. If you don\'t know it, you can find it by opening the Telegram app/web, clicking on the hamburguer menu, and then clicking on Settings. The username is the token preceded by a @.</li>' +
                '<li class="mb-2"><b>Copy your npub</b> here: <span class="text-xs">' + encodeNpub($NostrPublicKey) + '</span></li>' +
                '<li class="mb-2">Open the <b>Telegram room</b> of your choice and <b>paste the npub</b> there.</li>' +
                '<li class="mb-2">Right click (or tap-and-hold) over your message and select "Link to message".</li>' +
                '<li class="mb-2"><b>Paste</b> the URL in this screen.</li>' +
                '<li class="mb-2"><b>Click Add</b> to add the new identity to your Nostr profile and verify it.' +
            '</ol>' +
            '<p class="mt-6 mb-1 font-bold">Example of the URL you\'ll get:</p>' +
            '<p class="mt-1">https://t.me/nostr_protocol/118763</p>'
    };

    function addData() {
        if (!type || !url) {
            Info.set('You must enter the URL before adding');
            return;
        }

        if (!url.toLowerCase().startsWith('https')) {
            Info.set('URL must start with https');
            return;
        }

        let identityAlreadyExists = false;
        externalIdentities.forEach(identity => {
            if (identity.includes(type)) {
                identityAlreadyExists = true;
                return;
            }
        });
        if (identityAlreadyExists) {
            Info.set(type.charAt(0).toUpperCase() + type.slice(1) + ' identity already exists. Delete it first if you want to change it.');
            return;
        }

        let newEntry = '';

        const urlTokens = url.split('/');

        if (type === 'twitter') {
            if (urlTokens.length !== 6 || url.endsWith('/')) {
                Error.set("The Twitter/X URL that you provided for your verification message is not standard. It should have the form of this one: https://twitter.com/halfin/status/1110302988")
                return;
            }

            const user = urlTokens[3];
            const proof = urlTokens[5];
            newEntry = type + ':' + user + ':' + proof;
        } else if (type === 'github') {
            if (urlTokens.length !== 5 || url.endsWith('/')) {
                Error.set("The GitHub URL that you provided for your verification message is not standard. It should have the form of this one: https://gist.github.com/your_username/a3158dcaf61a1c49485zf1c2719469af")
                return;
            }

            const user = urlTokens[3];
            const proof = urlTokens[4];
            newEntry = type + ':' + user + ':' + proof;
        } else if (type === 'telegram') {
            if (!user) {
                Info.set('You must enter the Telegram username before adding');
                return;
            }
            if (urlTokens.length !== 5 || url.endsWith('/')) {
                Error.set("The Telegram URL that you provided for your verification message is not standard. It should have the form of this one: https://t.me/nostr_protocol/118763")
                return;
            }

            const channel = urlTokens[3];
            const proof = channel + '/' + urlTokens[4];
            newEntry = type + ':' + user + ':' + proof;
        }

        externalIdentities.push(newEntry);
        externalIdentities = externalIdentities;

        window.verifyHelp.close();

        url = '';
        user = '';

        changesMade = true;
    }

    function getMetadata() {
        if ($NostrPublicKey) {
            subscribeMetadata([$NostrPublicKey],
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
                () => {
                    lastProfileLoaded = true;
                });
        }
    }

    async function saveIdentitiesToNostr() {
        if (!changesMade) {
            Info.set('No changes made, so there is nothing to save')
        }
        if (!lastProfileLoaded) {
            Info.set('There was a problem loading your profile, so no changes are allowed. Reload the page and try again.')
            return;
        }

        // Filtering out 'i' tags to start clean
        let iFilteredProfileTags = profile.tags.filter(function(tag, index, arr){
            return tag[0] !== 'i';
        });

        // Adding current i tags to the profile
        externalIdentities.forEach(identity => {
            iFilteredProfileTags.push([
                'i',
                identity.split(':')[0] + ':' + identity.split(':')[1],
                identity.split(':')[2]
            ]);
        });

        profile.tags = iFilteredProfileTags;

        await publishMetadata(profile);      // Saving profile with new 'i' tags to Nostr

        await askAPIForVerification($NostrPublicKey);
    }

    onMount(() => {
        getMetadata();
    });
</script>

{#if loggedIn()}
    <h1>Adding a new external identity</h1>

    <div class="mt-4">
        <div class="flex space-x-2 mt-4">
            <select class="select-bordered select-info max-w-xs border rounded py-2 px-3" bind:value={type}>
                <option value="twitter">Twitter / X</option>
                <option value="github">GitHub</option>
                <option value="telegram">Telegram</option>
            </select>

            <button class="btn btn-square btn-outline btn-info tooltip" data-tip="Click to learn how to do it" on:click={() => {window.verifyHelp.showModal()}}>
                <Question />
            </button>

            {#if type === 'telegram'}
                <input class="input-info border rounded py-2 px-3" type="text" placeholder="Telegram user" bind:value={user}>
            {/if}
            <input class="w-2/3 input-info border rounded py-2 px-3" type="text" placeholder="URL" bind:value={url}>
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" on:click={addData}>Add</button>
        </div>
    </div>

    <div class="mt-16">
        <h2>External identities:</h2>
        {#if externalIdentities.length === 0}
            <p class="mt-2">Your Nostr profile doesn't have any external identity yet. Add one using the form above.</p>
        {/if}

        {#each externalIdentities as identity}
            <a class="flex hover:underline mt-5" target="_blank" href="{getExternalIdentityUrl(identity.split(':')[0], identity.split(':')[1], identity.split(':')[2])}">
                {#if identity.split(':')[0] === 'twitter'}
                    <Twitter />
                {:else if identity.split(':')[0] === 'github'}
                    <Github />
                {:else if identity.split(':')[0] === 'telegram'}
                    <Telegram />
                {/if}

                <div class="ml-2">{identity.split(':')[1]}</div>
            </a>
        {/each}

        {#if changesMade}
            <div class="mt-6">
                <button class="mt-4 py-2 px-4 bg-blue-500 hover:bg-blue-700 text-white font-bold rounded" on:click={saveIdentitiesToNostr}>Verify and Save</button>
            </div>
        {/if}
    </div>

{:else}
    <div class="w-full items-center justify-center text-center">
        <p>You still have to login to Plebeian Market.</p>
        <button class="btn btn-info mt-4" on:click={() => requestLoginModal()} on:keypress={() => requestLoginModal()}>Login</button>
    </div>
{/if}

<dialog id="verifyHelp" class="modal">
    <div class="modal-box w-11/12 max-w-5xl">
        <h3 class="font-bold text-lg">{verifyHelpInfo[type].title}</h3>
        <p class="py-4">{@html verifyHelpInfo[type].description}</p>
        <p class="py-4">
            {#if type === 'telegram'}
                <input class="input-info border rounded py-2 px-3" type="text" placeholder="Telegram user" bind:value={user}>
            {/if}
            <input class="input-info border rounded py-2 px-3" type="text" placeholder="URL" bind:value={url}>
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" on:click={addData}>Add</button>
        </p>
        <div class="modal-action">
            <form method="dialog">
                <button class="btn">Close</button>
            </form>
        </div>
    </div>
</dialog>