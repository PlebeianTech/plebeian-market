<script>
    import Time from 'svelte-time';

    export let auction = null;

    export let onEdit = (auction) => {};

    // TODO: perhaps move these functions inside here and have this component display the confirmation
    export let onCancel = (key) => {};
    export let onDelete = (key) => {};

    function copySnippet() {
        // TODO
        const snippet = '<link rel="stylesheet" href="https://plebeian.market/static/style.css">'
            + `<div id="plebeian-auction" data-key="${auction.key}"></div>`
            + '<script src="https://plebeian.market/app/buyer/bundle.js">'+ "</" + "script>";
        navigator.clipboard.writeText(snippet).then(() => alert("Snippet copied!"));
    }

    function view() {
        window.open(`/app/buyer#plebeian-auction-${auction.key}`, '_blank');
    }

    function start() {
        // TODO
    }
</script>

<div class="max-w-full p-4 rounded overflow-hidden shadow-lg bg-gray-900 my-3">
    <div class="text-center">
        <h3 class="text-zinc-300 text-2xl">{auction.title}</h3>
        <span class="text-zinc-300">
            {#if auction.started && !auction.ended}
                (running)
            {:else if auction.ended}
                (ended)
            {:else if auction.canceled}
                (canceled)
            {/if}
        </span>
    </div>
    <p class="text-zinc-300 mt-2">Duration: {auction.duration_str} {#if auction.start_date}/ <Time timestamp={auction.start_date} format="dddd MMMM D, H:mm" /> - <Time timestamp={auction.end_date} format="dddd MMMM D, H:mm - YYYY" />{/if}</p>
    <p class="text-zinc-300"><span>Starting bid: {auction.starting_bid}</span> <span>Reserve bid: {auction.reserve_bid}</span><span class="float-right">Bids: {auction.bids.length}</span></p>
    <div class="float-left pt-5">
        <div class="glowbutton glowbutton-copy" on:click|preventDefault={copySnippet}></div>
    </div>
    <div class="float-right pt-5">
        <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black" on:click={view}>View</button>
        {#if !auction.started}
            <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-green-800" on:click={start}>Start</button>
            {#if !auction.canceled}
                <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black" on:click={() => onEdit(auction)}>Edit</button>
            {/if}
            <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-red-800" on:click={() => onDelete(auction.key)}>Delete</button>
        {/if}
        {#if !auction.canceled && !auction.ended}
            <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-red-800" on:click={() => onCancel(auction.key)}>Cancel</button>
        {/if}
    </div>
</div>