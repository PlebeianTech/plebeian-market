<!--
    This is a store-based component to show a Login modal on the screen.

    You can request to open the login modal from everywhere by writing
    to the loginModalState:

    import { loginModalState } from "$lib/stores";

    loginModalState.set({
       openRequested: true,
       callbackFunc: function(){
          console.log("Login correct, now let's do real stuff");
          doSomethingUsefulAfterUserLoginCorrect();
       }
    });

    - For the modal to open, you need to set `openRequested` to true.
    - Also, you have to provide a callback function to be executed
        when/if the login is correct. If you don't want any action
        to be executed after login, just provide an empty function:

        loginModalState.set({
           openRequested: true,
           callbackFunc: () => {}
        });
-->
<svelte:options accessors />

<script lang="ts">
    import Login from "$lib/components/Login.svelte";
    import { loginModalState } from "$lib/stores";

    let login: Login | null;

    $: if ($loginModalState?.openRequested ?? false) {
        show($loginModalState.callbackFunc);
    }

    export function show(onLoginFunction) {
        if (typeof onLoginFunction === 'function') {
            onLogin = onLoginFunction;
        }

        login.startCheckingLogin();
    }

    export function hide() {
        login.stopCheckingLogin();

        loginModalState.set({
            openRequested: false,
            callbackFunc: () => {}
        });
    }

    export let onLogin: () => void = () => {};
</script>

<div class="modal" class:modal-open={$loginModalState?.openRequested ?? false}>
    <div class="modal-box relative flex justify-center items-center w-10/12 max-w-2xl">
        <label for="modal-box" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={() => hide()} on:keypress={() => hide()}>✕</label>
        <div class="w-full" style="margin-top: -40px" id="loginDiv">
            <Login
                    bind:this={login}
                    on:loginEvent={e => hide()}
                    on:loginTokenExpiredEvent={e => hide()}
                    {onLogin} />
        </div>
    </div>
</div>
