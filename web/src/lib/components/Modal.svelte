<svelte:options accessors />

<script lang="ts">
    export let content;

    export let hasHide: boolean = false;
    export let onHide: (saved: boolean) => void = (_) => { };

    export function show() {
        let toggle = <HTMLInputElement>document.getElementById('modal-toggle');
        if (toggle) {
            toggle.checked = true;
        }
    }

    export function hide(saved: boolean = false) {
        let toggle = <HTMLInputElement>document.getElementById('modal-toggle');
        if (toggle) {
            toggle.checked = false;
        }

        onHide(saved);
    }

    function onSave() {
        hide(true);
    }
</script>

<input type="checkbox" id="modal-toggle" for="modal-box" class="modal-toggle" />
<div class="modal">
    <div class="modal-box relative flex justify-center items-center w-10/12 max-w-1xl">
        <label for="modal-box" class:hidden={!hasHide} class="btn btn-sm btn-circle absolute right-2 top-2" on:click={() => hide()} on:keypress={() => hide()}>✕</label>
        <div class="w-full">
            <svelte:component this={content} onSave={onSave} />
        </div>
    </div>
</div>
