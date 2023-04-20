<script lang="ts">
    import { onMount } from 'svelte';
    import { getKeyFromKeyOrNpub, hasExtension } from "$lib/nostr/utils";
    import { ErrorHandler, putProfile, putVerify, getEntities, postEntity, deleteEntity } from "$lib/services/api";
    import { user, token, Info, Error } from "$lib/stores";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";
    import Loading from "$lib/components/Loading.svelte";
    import Plus from "$lib/components/icons/Plus.svelte";
    import X from "$lib/components/icons/X.svelte";
    import type { IEntity } from "$lib/types/base";
    import { ExternalAccountProvider } from "$lib/types/user";

    class Relay implements IEntity {
        id: number | null;
        url: string;

        key: string;
        endpoint = "users/me/relays";
        is_mine = true;

        constructor(id: number | null, url: string) {
            this.id = id;
            this.url = url;
            this.key = id !== null ? id.toString() : "";
        }

        public validate() {
            const colonIndex = this.url.indexOf(".");
            return !(this.url.length === 0) && colonIndex !== -1 && colonIndex !== this.url.length - 1;
        }

        public toJson() {
            return {url: this.url};
        }
    }

    function relayFromJson(json: any): Relay {
        return new Relay(<number>json.id, <string>json.url);
    }

    export let onSave: () => void = () => {};

    let nostrPublicKey: string = "";
    let nostrPublicKeyVerified: boolean = false;

    $: isValidInput = nostrPublicKey !== null && nostrPublicKey !== "";
    $: saveButtonActive = $user && isValidInput && !inRequest && nostrPublicKey !== $user.nostrPublicKey;

    let relays: Relay[] = [];
    let newRelay = new Relay(null, "");

    let inRequest = false;

    async function getKeyFromExtension() {
        nostrPublicKey = await (window as any).nostr.getPublicKey();
    }

    function save() {
        if (nostrPublicKey === null) {
            return;
        }

        let cleanKey = getKeyFromKeyOrNpub(nostrPublicKey);

        if (cleanKey === null) {
            Error.set("Invalid npub!");
            return;
        }

        inRequest = true;
        putProfile($token, {nostrPublicKey: cleanKey},
            u => {
                user.set(u);
                Info.set("Your Nostr public key has been saved!");
                inRequest = false;
                onSave();
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    let phrase: string = "";

    function verify() {
        inRequest = true;
        putVerify($token, ExternalAccountProvider.Nostr, false, phrase,
            () => {
                user.update(u => { if (u) { u.nostrPublicKeyVerified = true; } return u; });
                Info.set("Your Nostr key has been verified!");
                inRequest = false;
                onSave();
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    function resend() {
        inRequest = true;
        putVerify($token, ExternalAccountProvider.Nostr, true, undefined,
            () => {
                user.update(u => { if (u) { u.nostrVerificationPhraseSentAt = new Date(); } return u; });
                Info.set("Check your Nostr DM!");
                inRequest = false;
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    function loadRelays() {
        getEntities({endpoint: "users/me/relays", responseField: 'relays', fromJson: relayFromJson}, $token, e => relays = <Relay[]>e);
    }

    function addRelay() {
        if (newRelay.validate()) {
            inRequest = true;
            postEntity("users/me/relays", $token, newRelay,
                () => {
                    inRequest = false;
                    Info.set("Relay saved!");
                    newRelay = new Relay(null, "");
                    loadRelays();
                }, new ErrorHandler(true, () => inRequest = false));
        }
    }

    function removeRelay(r: Relay) {
        inRequest = true;
        deleteEntity($token, r,
            () => {
                inRequest = false;
                Info.set("Relay removed!");
                loadRelays();
            },
            new ErrorHandler(true, () => inRequest = false));
    }

    onMount(async () => {
        if ($user) {
            nostrPublicKey = $user.nostrPublicKey || "";
            nostrPublicKeyVerified = $user.nostrPublicKeyVerified;
            loadRelays();
        }
    });
</script>

<div class="text-2xl breadcrumbs">
    <ul>
        <li>Settings</li>
        <li>Nostr</li>
    </ul>
</div>

{#if inRequest}
    <Loading />
{/if}

{#if $user}
    {#if $user.nostrPublicKey && $user.nostrPublicKeyVerified && $user.nostrPublicKey === nostrPublicKey}
        <div class="w-full flex items-center justify-center mt-8">
            <div>
                <div class="text-2xl">Your verified Nostr public key is:</div>
                <div class="flex justify-center items-center gap-4">
                    <pre class="my-8 text-lg bg-base-300 text-center">{$user.nostrPublicKey}</pre>
                    <button class="btn btn-secondary" on:click={() => nostrPublicKey = ""}>Change</button>
                </div>
                <div>You can use any Nostr client that supports encrypted direct messages (NIP-04) to log in to the Plebeian Market backend.</div>
            </div>
        </div>
    {:else}
        <div class="w-full flex items-center justify-center mt-8">
            <div class="form-control w-full max-w-lg">
                <label class="label" for="nostr-public-key">
                    <span class="label-text">Nostr public key (HEX or NPUB formats accepted)</span>
                </label>
                <input bind:value={nostrPublicKey} id="nostr-public-key" name="nostr-public-key" type="text" class="bg-transparent z-10 ml-1.5 input input-bordered input-md w-full" />
            </div>
        </div>
        <div class="w-full flex items-center justify-center mt-4 gap-5">
            {#if hasExtension()}
                <button class="btn" class:btn-primary={nostrPublicKey === null} class:btn-secondary={nostrPublicKey !== null} class:btn-disabled={inRequest} on:click={getKeyFromExtension}>Get from extension</button>
            {/if}
        </div>

        <div class="flex justify-center items-center mt-4 h-15">
            <button id="save-profile" class="btn btn-primary" class:btn-disabled={!saveButtonActive} on:click|preventDefault={save}>Save</button>
        </div>
    {/if}
    {#if $user.nostrPublicKey && !$user.nostrPublicKeyVerified}
        <div class="mt-4">
            {#if $user && !$user.nostrVerificationPhraseSentAt}
                <InfoBox>
                    <span>We will send the verification phrase over encrypted DM.</span>
                </InfoBox>
                <div class="w-full flex items-center justify-center mt-4">
                    <div class="form-control w-full max-w-lg">
                        <button class="btn btn-primary" on:click={resend} disabled={inRequest}>Send</button>
                    </div>
                </div>
            {:else}
                <InfoBox>
                    <span>Please enter the three BIP-39 words we sent to you over Nostr DM.</span>
                </InfoBox>
                <div class="w-full flex items-center justify-center mt-4">
                    <div class="form-control w-full max-w-full">
                        <label class="label" for="title">
                            <span class="label-text">Verification phrase</span>
                        </label>
                        <input bind:value={phrase} type="text" name="phrase" class="input input-lg input-bordered" />
                    </div>
                </div>
                <div class="flex justify-center items-center mt-4 h-24 gap-5">
                    <button id="verify-nostr" class="btn btn-primary" class:btn-disabled={inRequest} on:click|preventDefault={verify}>Verify</button>
                    <button class="btn" on:click={resend} disabled={inRequest}>Resend</button>
                </div>
            {/if}
        </div>
    {/if}
    <div class="divider"></div>
    <h2 class="text-3xl">Relays</h2>
    <div>
        {#each relays as relay}
            <div class="mt-3 flex">
                <pre>{relay.url}</pre>
                <div class="btn btn-circle btn-xs btn-error ml-1" on:click={() => removeRelay(relay)} on:keypress={() => removeRelay(relay)}><X /></div>
            </div>
        {/each}
        <div class="flex justify-center items-center mt-6 gap-4">
            <div class="flex flex-col">
                <input type="text" bind:value={newRelay.url} placeholder="add a relay" class="input input-bordered input-primary w-full max-w-xs" on:keypress={(e) => { if (e.key === "Enter") addRelay(); }} />
            </div>
            <div>
                <button class="btn btn-s btn-circle btn-ghost" class:btn-disabled={!newRelay.validate()} on:click={addRelay}><Plus /></button>
            </div>
        </div>
    </div>
{/if}
