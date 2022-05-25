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
            <div class="flex lg:block items-center label-text w-full text-right text-error mr-2">
                <span>I am sure!</span>
                <span class="inline-block invisible w-0 lg:visible lg:w-auto">&nbsp;I want to delete this auction!</span>
            </div>
            <input type="checkbox" class="toggle toggle-secondary toggle-lg" bind:value={confirm} />
        </label>
    </div>
    <button class="btn mx-2" on:click|preventDefault={onCancel}>Cancel</button>
    <button class="btn btn-error mx-2" on:click|preventDefault={check}>Delete</button>
</div>
