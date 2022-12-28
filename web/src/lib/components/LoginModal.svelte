<svelte:options accessors />

<script lang="ts">
    import Login from "$lib/components/Login.svelte";

    let login : Login | null;

    export let content;

    export let id = 'login-modal';

    export let loginModalVisible = false;

    export function show(onLoginFunction) {
        if (!loginModalVisible) {
            loginModalVisible = true;

            if (typeof onLoginFunction === 'function') {
                onLogin = onLoginFunction;
            }

            login.startCheckingLogin();

            let toggle = <HTMLInputElement>document.getElementById(`${id}-toggle`);
            if (toggle) {
                toggle.checked = true;
            }
        }
    }

    export function hide() {
        login.stopCheckingLogin();

        loginModalVisible = false;

        let toggle = <HTMLInputElement>document.getElementById(`${id}-toggle`);
        if (toggle) {
            toggle.checked = false;
        }
    }

    export let onLogin: () => void = () => {};
</script>

<input type="checkbox" id="{id}-toggle" for="modal-box" class="modal-toggle" />
<div class="modal">
    <div class="modal-box relative flex justify-center items-center w-10/12 max-w-2xl">
        <label for="modal-box" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={() => hide()} on:keypress={() => hide()}>✕</label>
        <div class="w-full" style="margin-top: -40px">
            <Login bind:this={login} on:loginEvent={e => hide()} {onLogin} />
        </div>
    </div>
</div>
