<script lang="ts">
    import { onMount } from 'svelte';
    import { ErrorHandler, getEntities, postEntity, deleteEntity } from "$lib/services/api";
    import { user, Info } from "$lib/stores";
    import { token } from "$sharedLib/stores";
    import Loading from "$lib/components/Loading.svelte";
    import Plus from "$sharedLib/components/icons/Plus.svelte";
    import X from "$sharedLib/components/icons/X.svelte";
    import type { IEntity } from "$lib/types/base";

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
            return JSON.stringify({url: this.url});
        }
    }

    function relayFromJson(json: any): Relay {
        return new Relay(<number>json.id, <string>json.url);
    }

    export const onSave: () => void = () => {};

    let relays: Relay[] = [];
    let newRelay = new Relay(null, "");

    let inRequest = false;

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
    <h2 class="text-3xl my-4">Relays</h2>
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
