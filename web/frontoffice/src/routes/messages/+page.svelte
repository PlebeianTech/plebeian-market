<script>
    import {NostrPublicKey, privateMessages} from "$lib/stores";
    import {onMount} from "svelte";
    import {checkExtensionOrShowDialog} from "$lib/services/nostr";
    import {nip19} from "nostr-tools";
    import SimpleNote from "$lib/components/nostr/SimpleNote.svelte";

    let selectedConversationPubkey = null;

    let sortedMessages = [];

    onMount(async () => {
        if (!$NostrPublicKey) {
            if (checkExtensionOrShowDialog()) {
                $NostrPublicKey = await window.nostr.getPublicKey();
            }
        }
    });

    $: {
        if ($privateMessages.human && $privateMessages.human[selectedConversationPubkey]) {
            sortedMessages = Object.entries($privateMessages.human[selectedConversationPubkey]).sort((a, b) => {
                return a[1].created_at - b[1].created_at;
            });
        } else {
            sortedMessages = [];
        }
    }
</script>

<svelte:head>
    <title>Messages</title>
</svelte:head>

<h1 class="text-center text-3xl lg:text-3xl mt-12 mb-4 lg:mt-12 lg:mb-12 p-4">Messages</h1>

<div class="flex flex-col w-full lg:flex-row">
    <div class="grid flex-grow h-fit card bg-base-300 rounded-box place-items-center drawer drawer-mobile w-1/3 p-6">
            <input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
            <div class="drawer-content flex flex-col items-center justify-center">
                <!-- Page content here -->
                <label for="my-drawer-2" class="btn btn-primary drawer-button lg:hidden">Open drawer</label>
            </div>
            <div class="drawer-side">
                <label for="my-drawer-2" class="drawer-overlay"></label>
                <ul class="menu p-4 text-base-content">
                    {#each Object.entries($privateMessages.human ?? []) as [privateKey, message]}
                        <li class="rounded-lg"
                            class:bg-primary={selectedConversationPubkey === privateKey}
                            on:click={() => selectedConversationPubkey = privateKey}
                        >
                            <a>{nip19.npubEncode(privateKey)}</a>
                        </li>
                    {/each}
                </ul>
            </div>

    </div>

    <div class="divider lg:divider-horizontal"></div>

    <div class="grid flex-grow h-fit card bg-base-300 rounded-box w-2/3 p-6
         flex flex-col mt-2 mb-6 pb-6 bg-cover bg-top bg-info-content-200 gap-2 overflow-x-hidden overflow-y-auto w-full"
         style="background-size: 5px 5px; background-image: radial-gradient(hsla(var(--bc)/.2) 0.5px,hsla(var(--b2)/1) 0.5px);">
            {#each sortedMessages as [publicKey, message]}
                <SimpleNote {message} />
            {/each}
    </div>
</div>



