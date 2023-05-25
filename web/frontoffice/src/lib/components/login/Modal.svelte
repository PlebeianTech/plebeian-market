<!--
    This is a store-based component to show a Login modal on the screen.

    You can request to open the login modal from everywhere by calling
    the helper function:

    import { requestLoginModal } from "$lib/utils";

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
    import NostrLogin from "$lib/components/login/Nostr.svelte";
    import { loginModalState } from "$lib/stores";

    let open = false;

    $: if ($loginModalState.openRequested) {
        show($loginModalState.callbackFunc);

        $loginModalState.openRequested = false
    }

    export function show(onLoginFunction) {
        open = true;

        if (typeof onLoginFunction === 'function') {
            onLogin = onLoginFunction;
        }
    }

    export function hide() {
        open = false;
    }

    export let onLogin: () => void = () => {};
</script>

<div class="modal" class:modal-open={open}>
    <div class="modal-box relative flex justify-center items-center w-11/12 max-w-2xl">
        <label for="modal-box" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={() => hide()} on:keypress={() => hide()}>✕</label>
        <div class="w-full" id="loginDiv">
            {#if open}
                <NostrLogin {onLogin} on:login={hide} />
            {/if}
        </div>
    </div>
</div>
