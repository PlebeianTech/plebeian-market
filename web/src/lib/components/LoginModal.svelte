<svelte:options accessors />

<script lang="ts">
    import Login from "$lib/components/Login.svelte";

    let login : Login | null;
    let isModalOpen = false;

    export function show(onLoginFunction) {
        if (typeof onLoginFunction === 'function') {
            onLogin = onLoginFunction;
        }

        login.startCheckingLogin();

        isModalOpen = true;
    }

    export function hide() {
        login.stopCheckingLogin();

        isModalOpen = false;
    }

    export let onLogin: () => void = () => {};
</script>

<div class="modal" class:modal-open={isModalOpen}>
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
