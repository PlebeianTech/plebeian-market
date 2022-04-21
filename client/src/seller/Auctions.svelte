<script>
    import { onMount } from 'svelte';
    import dayjs from 'dayjs';
    import Time from 'svelte-time';
    import { token, fromJson, fetchAPI } from "../common.js";

    function emptyAuction() {
        return {
            starting_bid: 10000,
            reserve_bid: 10000,
            start_date: dayjs(new Date()).startOf('day').add(1, 'day').format("YYYY-MM-DDTHH:mm"),
            end_date: dayjs(new Date()).startOf('day').add(2, 'days').format("YYYY-MM-DDTHH:mm")
        };
    }

    let confirmation = null;
    let auction = null;
    let isEdit = false;
    let auctions = [];

    function asJson() {
        var json = {};
        for (var k in auction) {
            if (k === 'canceled') {
                continue;
            }
            if (k === 'start_date' || k === 'end_date') {
                json[k] = dayjs(auction[k]).toISOString();
            } else {
                json[k] = auction[k];
            }
        }
        return JSON.stringify(json);
    }

    function checkResponse(response) {
        if (response.status === 200) {
            confirmation = null;
            auction = null;
            response.json().then(data => {
                if (data.auctions) {
                    auctions = data.auctions.map(fromJson);
                } else {
                    fetchAPI("/auctions", 'GET', $token, null, checkResponse);
                }
            });
        } else if (response.status === 401) {
            console.log("Error 401: Unauthorized");
            $token = null;
        } else {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.indexOf('application/json') !== -1) {
                return response.json().then(data => { alert(`Error: ${data.message}`); });
            } else {
                return response.text().then(text => { console.log(`Error ${response.status}: ${text}`); });
            }
        }
    }

    function createAuction() {
        fetchAPI("/auctions", 'POST', $token, asJson(), checkResponse);
    }

    function deleteAuction(key) {
        confirmation = {
            message: "Type DELETE MY AUCTION below to continue...",
            input: "",
            continue: () => {
                if (confirmation.input === "DELETE MY AUCTION") {
                    fetchAPI(`/auctions/${key}`, 'DELETE', $token, null, checkResponse);
                } else {
                    console.log(`Wrong input: ${confirmation.input}...`)
                }
            },
            close: () => {confirmation = null}};
    }

    function cancelAuction(key) {
        confirmation = {
            message: "Type CANCEL MY AUCTION below to continue...",
            input: "",
            continue: () => {
                if (confirmation.input === "CANCEL MY AUCTION") {
                    fetchAPI(`/auctions/${key}`, 'PUT', $token, JSON.stringify({'canceled': true}), checkResponse);
                } else {
                    console.log(`Wrong input: ${confirmation.input}...`)
                }
            },
            close: () => {confirmation = null}
        };
    }

    function updateAuction () {
        fetchAPI(`/auctions/${auction.key}`, 'PUT', $token, asJson(), checkResponse);
    }

    function startEdit(a) {
        isEdit = true;
        auction = a;
    }

    function cancelEdit() {
        auction = null;
    }

    function startCreate() {
        isEdit = false;
        auction = emptyAuction();
    }

    function copyAuction(key) {
        const snippet = '<link rel="stylesheet" href="https://plebeian.market/static/style.css">'
            + `<div id="plebeian-auction" data-key="${key}"></div>`
            + '<script src="https://plebeian.market/app/buyer/bundle.js">'+ "</" + "script>";
        navigator.clipboard.writeText(snippet).then(() => alert("Snippet copied!"));
    }

    function openAuction(key) {
        window.open(`/app/buyer#plebeian-auction-${key}`, '_blank');
    }

    onMount(async () => { fetchAPI("/auctions", 'GET', $token, null, checkResponse); });
</script>

<div class="pt-10 flex justify-center items-center">
<section class="w-3/5">
        {#if confirmation}
        <div class="max-w-full p-4 rounded shadow-lg bg-red-700 my-3">
            <h3 class="mb-4 text-2xl text-center text-white">{confirmation.message}</h3>
            <div class="flex items-center justify-center">
                <input type="text" class="form-control text-3xl rounded" bind:value={confirmation.input} />
            </div>
        </div>
        <div class="float-left pt-5">
            <div class="glowbutton glowbutton-continue" on:click|preventDefault={confirmation.continue}></div>
        </div>
        <div class="float-right pt-5">
            <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black" on:click|preventDefault={confirmation.close}>Cancel</button>
        </div>
        {:else if auction}
        <div class="max-w-full p-4 rounded shadow-lg bg-gray-900 my-3 glowbox">
                <h3 class="mb-4 text-2xl text-center text-white">{#if isEdit}Edit auction <code class="bg-cyan-600 p-1 rounded">{auction.key}</code>{:else}Create a new auction{/if}</h3>
                <form id="new-auction">
                    <div class="flex">
                        <div class="form-group mr-2">
                            <input class="form-field" type="datetime-local" name="start-date" bind:value={auction.start_date} />
                            <label class="form-label" for="start-date">Start</label>
                        </div>
                        <div class="ml-2">
                            <button class="mr-2 mt-5 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black float-left hidden md:inline-block" on:click|preventDefault={() => auction.start_date = dayjs(new Date()).format("YYYY-MM-DDTHH:mm")}>Now</button>
                            <button class="mr-2 mt-5 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black float-left hidden md:inline-block" on:click|preventDefault={() => auction.start_date = dayjs(new Date()).add(5, 'minutes').format("YYYY-MM-DDTHH:mm")}>In 5 minutes</button>
                            <button class="mr-2 mt-5 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black float-left hidden md:inline-block" on:click|preventDefault={() => auction.start_date = dayjs(new Date()).startOf('day').add(1, 'day').format("YYYY-MM-DDTHH:mm")}>At midnight</button>
                        </div>
                    </div>
                    <div class="flex">
                        <div class="form-group mr-2">
                            <input class="form-field" type="datetime-local" name="end-date" bind:value={auction.end_date} />
                            <label class="form-label" for="end-date">End</label>
                        </div>
                        <div class="ml-2">
                            <button class="mr-2 mt-5 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black float-left hidden md:inline-block" on:click|preventDefault={() => auction.end_date = dayjs(auction.start_date).add(1, 'hour').format("YYYY-MM-DDTHH:mm")}>An hour</button>
                            <button class="mr-2 mt-5 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black float-left hidden md:inline-block" on:click|preventDefault={() => auction.end_date = dayjs(auction.start_date).add(1, 'day').format("YYYY-MM-DDTHH:mm")}>A day</button>
                            <button class="mr-2 mt-5 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black float-left hidden md:inline-block" on:click|preventDefault={() => auction.end_date = dayjs(auction.start_date).add(1, 'week').format("YYYY-MM-DDTHH:mm")}>A week</button>
                        </div>
                    </div>
                    <div class="flex">
                        <div class="form-group mr-2">
                            <input class="form-field" name="starting-bid" bind:value={auction.starting_bid} type="number" id="starting-bid" />
                            <label class="form-label" for="starting-bid">Starting bid</label>
                        </div>
                        <div class="form-group ml-2">
                            <input class="form-field" name="reserve-bid" bind:value={auction.reserve_bid} type="number" id="reserve-bid" />
                            <label class="form-label" for="reserve-bid">Reserve bid</label>
                        </div>
                    </div>
                </form>
        </div>
        <div class="float-left pt-5">
            {#if isEdit}
                <div class="glowbutton glowbutton-save" on:click|preventDefault={updateAuction}></div>
            {:else}
                <div class="glowbutton glowbutton-save" on:click|preventDefault={createAuction}></div>
            {/if}                                
        </div>
        <div class="float-right pt-5">
            <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black" on:click|preventDefault={cancelEdit}>Cancel</button>
        </div>
        {:else}
        <div class="flex items-center justify-center">
            <div class="glowbutton glowbutton-create" on:click|preventDefault={startCreate}></div>
        </div>
            {#each auctions as a}
            <div class="max-w-full p-4 rounded overflow-hidden shadow-lg bg-gray-900 my-3">
                <p class="text-center">
                    <code class="bg-cyan-600 p-1 rounded">{ a.key }</code>
                    <span class="text-zinc-300">
                        {#if a.started && !a.ended}
                            (running)
                        {:else if a.ended}
                            (ended)
                        {:else if a.canceled}
                            (canceled)
                        {/if}
                    </span>
                </p>
                <p class="text-zinc-300 mt-2">From <Time timestamp={ a.start_date } format="dddd MMMM D, H:mm" /> - <Time timestamp={ a.end_date } format="dddd MMMM D, H:mm - YYYY" /></p>
                <p class="text-zinc-300"><span>Starting bid: { a.starting_bid }</span> <span>Reserve bid: { a.reserve_bid }</span><span class="float-right">Bids: { a.bids.length }</span></p>
                <div class="float-left pt-5">
                    <div class="glowbutton glowbutton-copy" on:click|preventDefault={copyAuction(a.key)}></div>
                </div>
                <div class="float-right pt-5">
                    <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-green-800" on:click={openAuction(a.key)}>Open</button>
                    {#if !a.started}
                        {#if !a.canceled}
                            <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black" on:click={startEdit(a)}>Edit</button>
                        {/if}
                        <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-red-800" on:click={deleteAuction(a.key)}>Delete</button>
                    {/if}
                    {#if !a.canceled && !a.ended}
                        <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-red-800" on:click={cancelAuction(a.key)}>Cancel</button>
                    {/if}
                </div>
            </div>
            {/each}
        {/if}
</section>
</div>