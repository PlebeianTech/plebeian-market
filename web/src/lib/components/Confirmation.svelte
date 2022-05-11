<script lang="ts">
    export let message = null;
    export let expectedInput = null;

    export let onCancel = () => {};
    export let onContinue = () => {};

    let input = null;

    function checkInput() {
        if (input === expectedInput) {
            onContinue();
        } else {
            console.log(`Wrong input: ${input}...`)
        }
    }
</script>

<div class="bg-warn flex items-center justify-center w-full">
    <input type="text" placeholder="Type {expectedInput} here!" class="input input-bordered input-warning mx-1 w-full" bind:value={input} />
    <button class="btn mx-2" on:click|preventDefault={onCancel}>Cancel</button>
    <button class="btn btn-warning mx-2" on:click|preventDefault={checkInput}>Delete</button>
</div>
