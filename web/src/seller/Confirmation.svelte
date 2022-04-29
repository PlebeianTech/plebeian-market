<script>
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

<div class="max-w-full p-4 rounded shadow-lg bg-red-700 my-3">
    <h3 class="mb-4 text-2xl text-center text-white">{message}</h3>
    <div class="flex items-center justify-center">
        <input type="text" class="form-control text-3xl rounded" bind:value={input} />
    </div>
</div>
<div class="float-left pt-5">
    <div class="glowbutton glowbutton-continue" on:click|preventDefault={checkInput}></div>
</div>
<div class="float-right pt-5">
    <button class="btn" on:click|preventDefault={onCancel}>Cancel</button>
</div>