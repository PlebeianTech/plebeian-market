<svelte:options accessors />

<script lang="ts">
    export let content;

    export let id = 'login-modal';

    export function show() {
        let toggle = <HTMLInputElement>document.getElementById(`${id}-toggle`);
        if (toggle) {
            toggle.checked = true;
        }
    }

    export function hide() {
        let toggle = <HTMLInputElement>document.getElementById(`${id}-toggle`);
        if (toggle) {
            toggle.checked = false;
        }
    }

    export let onLogin: () => void = () => {};
</script>

<input type="checkbox" id="{id}-toggle" for="modal-box" class="modal-toggle" />
<div class="modal">
    <div class="modal-box relative flex justify-center items-center w-10/12 max-w-1xl">
        <label for="modal-box" class="btn btn-sm btn-circle absolute right-2 top-2" on:click={() => hide()} on:keypress={() => hide()}>✕</label>
        <div class="w-full">
            <svelte:component this={content} {onLogin} />
        </div>
    </div>
</div>
