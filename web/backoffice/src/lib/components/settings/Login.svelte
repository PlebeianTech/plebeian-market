<script lang="ts">
    import { page } from '$app/stores';
    import { user } from "$lib/stores";
    import LightningLoginSettings from "$lib/components/settings/LightningLogin.svelte";

    export let onSave: () => void = () => {};
</script>

{#if $page.url.pathname === "/admin/account/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>Login</li>
        </ul>
    </div>
{/if}

{#if $user}
    {#if $user.nostrPublicKey}
        <h2 class="text-3xl my-4">Nostr</h2>

        <div class="w-full flex items-center justify-center mt-8">
            <div>
                <div class="text-2xl">Your verified Nostr public key is:</div>
                <div class="flex justify-center items-center gap-4">
                    <pre class="my-8 text-lg bg-base-300 text-center">{$user.nostrPublicKey}</pre>
                </div>
                <div>You can log in to the Plebeian Market Stall Manager using Nostr.</div>
            </div>
        </div>

        <div class="divider"></div>
    {/if}

    <h2 class="text-3xl my-4">Lightning</h2>

    <LightningLoginSettings />
{/if}
