<script lang="ts">
    export let onCancel = () => {};
    export let onContinue = () => {};

    let confirm = false;

    function check() {
        if (confirm) {
            onContinue();
        }
    }
</script>

<label class="label cursor-pointer">
    <div class="items-center label-text w-full text-right text-error mr-2">
        YES!
    </div>
    <input type="checkbox" class="toggle toggle-secondary toggle-lg" bind:value={confirm} />
</label>
<button class="btn mx-1" on:click|preventDefault={onCancel}>Cancel</button>
<button class="btn btn-error mx-1" on:click|preventDefault={check}>Delete</button>
