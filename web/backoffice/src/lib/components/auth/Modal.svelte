<!--
    This is a store-based component to show a Login modal on the screen.

    You can request to open the login modal from everywhere using:

    import { AuthRequired } from "$lib/stores";

    AuthRequired.set({
        cb: () => {
            console.log("Login correct, now let's do real stuff");
            doSomethingUsefulAfterUserLoginCorrect();
        }
    });

    You can provide a callback function to be executed when/if
    the users login correctly as in the previous example. If you
    don't want any action to be executed after login, just pass "true":

    AuthRequired.set(true);
-->
<svelte:options accessors />

<script lang="ts">
    import AuthChoice from "$lib/components/auth/Choice.svelte";
    import { type AuthCallback, AuthRequired, AuthBehavior } from "$lib/stores";

    let open = false;
    let behavior: AuthBehavior = AuthBehavior.Login;

    $: if ($AuthRequired !== false) {
        behavior = $AuthRequired === true || $AuthRequired.default === undefined ? AuthBehavior.Login : $AuthRequired.default;

        show($AuthRequired === true || $AuthRequired.cb === undefined ? () => {} : $AuthRequired.cb);

        AuthRequired.set(false);
    }

    export function show(cb: AuthCallback) {
        onLogin = cb;
        open = true;
    }

    export function hide() {
        open = false;
    }

    export let onLogin: () => void = () => {};
</script>

<div class="modal" class:modal-open={open}>
    <div class="modal-box relative flex justify-center items-center w-10/12 max-w-2xl">
        <label for="modal-box" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={() => hide()} on:keypress={() => hide()}>✕</label>
        <div class="w-full" id="loginDiv">
            {#if open}
                <AuthChoice {behavior} on:login={hide} on:loginTokenExpiredEvent={_ => hide()} {onLogin} />
            {/if}
        </div>
    </div>
</div>
