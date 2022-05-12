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

<div class="bg-warn flex items-center justify-center w-full">
    <div class="form-control w-full">
        <label class="label cursor-pointer">
            <span class="label-text w-full text-right text-error mr-2">I am sure I want to delete this auction</span> 
            <input type="checkbox" class="toggle toggle-secondary toggle-lg" bind:value={confirm} />
        </label>
    </div>
    <button class="btn mx-2" on:click|preventDefault={onCancel}>Cancel</button>
    <button class="btn btn-error mx-2" on:click|preventDefault={check}>Delete</button>
</div>
