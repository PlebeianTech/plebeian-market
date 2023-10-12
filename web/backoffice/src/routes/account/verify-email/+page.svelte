<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import { ErrorHandler, putVerify } from "$lib/services/api";
    import { ExternalAccountProvider } from "$lib/types/user";
    import { Info, token } from "$sharedLib/stores";

    let params = {};

    let missingToken = false;
    let missingPhrase = false;
    let verificationFailed = false;

    onMount(async () => {
        let parts = $page.url.href.split("#");
        if (parts.length === 2) {
            for (let kv of parts[1].split("&")) {
                let [k, v] = kv.split("=");
                params[k] = v;
            }
        }

        let tokenFromRequest = params['token'];

        if (tokenFromRequest === null) {
            missingToken = true;
        } else if (params['phrase'] === undefined || params['phrase'] === null || params['phrase'] == "") {
            missingPhrase = true;
        } else {
            putVerify(tokenFromRequest, ExternalAccountProvider.Email, false, params['phrase'].replaceAll("%20", " "),
                () => {
                    Info.set("Your email address has been verified!");
                    token.set(tokenFromRequest);
                    localStorage.setItem('token', tokenFromRequest);
                    goto("/admin");
                },
                new ErrorHandler(true, () => { verificationFailed = true; }));
        }
    });
</script>

{#if missingToken}
    <div class="text-4xl">You are not logged in!</div>
{:else if missingPhrase}
    <div class="text-4xl">Invalid URL!</div>
{:else if verificationFailed}
    <div class="text-4xl">Verification failed!</div>
{/if}