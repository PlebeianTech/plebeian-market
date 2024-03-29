<!--
    This is a store-based component to show a Login modal on the screen.

    You can request to open the login modal from everywhere by calling
    the helper function:

    import { requestLoginModal } from "$sharedLib/utils";

    requestLoginModal(() => {
        console.log("Login correct, now let's do real stuff");
        doSomethingUsefulAfterUserLoginCorrect();
    });

    You can provide a callback function to be executed when/if
    the users login correctly as in the previous example. If you
    don't want any action to be executed after login, left the
    parameter empty and call it this way:

    requestLoginModal();

-->
<svelte:options accessors />

<script lang="ts">
    import NostrLogin from "./Nostr.svelte";
    import {
        NostrPrivateKey,
        NostrPublicKey,
        NostrLoginMethod,
        loginModalState,
        token,
        userChosenCurrency
    } from "$sharedLib/stores";
    import {onMount} from "svelte";

    let open = false;

    $: if ($loginModalState.openRequested) {
        show($loginModalState.loginSuccessCB, $loginModalState.loginBackofficeSuccessCB);

        $loginModalState.openRequested = false
    }

    /*
    Disabling auto-close login modal when already logged-in for now
    $: if (open && $NostrPublicKey && $NostrLoginMethod) {
        hide();
    }
    */

    export function show(loginSuccessCB: () => void = () => {}, loginBackofficeSuccessCB: () => void = () => {}) {
        open = true;

        onLogin = loginSuccessCB;
        onLoginBackoffice = loginBackofficeSuccessCB;
    }

    export function hide() {
        open = false;
    }

    export let onLogin: () => void = () => {};
    export let onLoginBackoffice: () => void = () => {};

    onMount(async () => {
        $NostrPublicKey =   localStorage.getItem("nostrPublicKey");
        $NostrPrivateKey =  localStorage.getItem("nostrPrivateKey");
        $token =            localStorage.getItem("token");
        $NostrLoginMethod = localStorage.getItem("nostrLoginMethod");
        $userChosenCurrency = localStorage.getItem("userChosenCurrency") ?? 'USD';
    });
</script>

<div class="modal" class:modal-open={open}>
    <div class="modal-box relative flex justify-center items-center w-11/12 max-w-5xl p-6 lg:p-9">
        <label class="btn btn-sm btn-circle absolute right-2 top-2" on:click={() => hide()} on:keypress={() => hide()}>✕</label>
        <div class="w-full" id="loginDiv">
            {#if open}
                <NostrLogin on:login={onLogin} on:backoffice-login={onLoginBackoffice} on:close={hide} />
            {/if}
        </div>
    </div>
</div>
