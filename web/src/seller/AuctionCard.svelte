<script>
    import Time from 'svelte-time';
    import { fetchAPI, fromJson } from "../common.js";
    import { token } from "../stores.js";

    export let auction = null;
    let twitterLinkCopied = false;

    export let onEdit = (auction) => {};

    // TODO: perhaps move these functions inside here and have this component display the confirmation
    export let onCancel = (key) => {};
    export let onDelete = (key) => {};

    function copySnippet() {
        navigator.clipboard.writeText(`/app/buyer#plebeian-auction-${auction.key}`).then(() => { twitterLinkCopied = true; alert("URL copied!"); });
    }

    function view() {
        window.open(`/app/buyer#plebeian-auction-${auction.key}`, '_blank');
    }

    function start() {
        fetchAPI(`/auctions/${auction.key}/start-twitter`, 'PUT', $token, null,
            (response) => {
                if (response.status === 200) {
                    fetchAPI(`/auctions/${auction.key}`, 'GET', $token, null,
                        (auctionResponse) => {
                            if (auctionResponse.status === 200) {
                                auctionResponse.json().then(data => {
                                    auction = fromJson(data.auction);
                                });
                            }
                        }
                    );
                }
            }
        );
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
    <div class="mt-2 float-root">
        <div class="py-5 float-right">
            <button class="btn" on:click={view}>View</button>
            {#if !auction.started}
                {#if !auction.canceled}
                    <button class="btn" on:click={() => onEdit(auction)}>Edit</button>
                {/if}
                <button class="btn" on:click={() => onDelete(auction.key)}>Delete</button>
            {/if}
            {#if !auction.canceled && !auction.ended}
                <button class="btn" on:click={() => onCancel(auction.key)}>Cancel</button>
            {/if}
        </div>
    </div>
    <div class="mt-2">
        <div class="py-5 w-full flex items-center justify-center bg-gray-800 rounded">
            <p class="text-zinc-300 text-2xl mr-2">Twitter</p>
            {#if !twitterLinkCopied && !auction.started}
                <div class="glowbutton glowbutton-copy mx-2" on:click|preventDefault={copySnippet}></div>
            {:else}
                <button class="btn mx-2" on:click={copySnippet}>Copy</button>
            {/if}
            {#if !auction.started}
                <div class="flex justify-center items-center">
                    the link,
                    <span class="mx-2 inline-block w-[50px] h-[50px]">
                        <svg viewBox="328 355 335 276" xmlns="http://www.w3.org/2000/svg">
                            <path d="
                              M 630, 425
                              A 195, 195 0 0 1 331, 600
                              A 142, 142 0 0 0 428, 570
                              A  70,  70 0 0 1 370, 523
                              A  70,  70 0 0 0 401, 521
                              A  70,  70 0 0 1 344, 455
                              A  70,  70 0 0 0 372, 460
                              A  70,  70 0 0 1 354, 370
                              A 195, 195 0 0 0 495, 442
                              A  67,  67 0 0 1 611, 380
                              A 117, 117 0 0 0 654, 363
                              A  65,  65 0 0 1 623, 401
                              A 117, 117 0 0 0 662, 390
                              A  65,  65 0 0 1 630, 425
                              Z"
                              style="fill:#3BA9EE;"/>
                        </svg>
                    </span>
                    it, then click
                </div>
                {#if !twitterLinkCopied}
                    <button class="btn ml-2" on:click={start}>Start</button>
                {:else}
                    <div class="glowbutton glowbutton-start ml-2" on:click|preventDefault={start}></div>
                {/if}
            {/if}
        </div>
    </div>
</div>