<script>
    import { onMount } from 'svelte';
    import Time from 'svelte-time';
    import { token, fromJson, fetchAPI } from "../common.js";

    function emptyAuction() {
        return {
            title: "",
            description: "",
            starting_bid: 0,
            reserve_bid: 0,
            duration_hours: 24
        };
    }

    let confirmation = null;
    let currentAuction = null;
    let isEdit = false;
    let auctions = [];

    function asJson() {
        var json = emptyAuction();
        for (var k in currentAuction) {
            if (k in json) {
                json[k] = currentAuction[k];
            }
        }
        return JSON.stringify(json);
    }

    function checkResponse(response) {
        if (response.status === 200) {
            confirmation = null;
            currentAuction = null;
            response.json().then(data => {
                if (data.auctions) {
                    auctions = data.auctions.map(fromJson);
                    if (!auctions.length) {
                        startCreate();
                    }
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
        currentAuction.invalidTitle = currentAuction.title.length === 0;
        currentAuction.invalidDescription = currentAuction.description.length === 0;
        if (currentAuction.invalidTitle || currentAuction.invalidDescription) {
            return;
        }

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
        fetchAPI(`/auctions/${currentAuction.key}`, 'PUT', $token, asJson(), checkResponse);
    }

    function startEdit(a) {
        isEdit = true;
        currentAuction = a;
    }

    function cancelEdit() {
        currentAuction = null;
    }

    function startCreate() {
        isEdit = false;
        currentAuction = emptyAuction();
    }

    function copyAuction(key) {
        // TODO
        const snippet = '<link rel="stylesheet" href="https://plebeian.market/static/style.css">'
            + `<div id="plebeian-auction" data-key="${key}"></div>`
            + '<script src="https://plebeian.market/app/buyer/bundle.js">'+ "</" + "script>";
        navigator.clipboard.writeText(snippet).then(() => alert("Snippet copied!"));
    }

    function viewAuction(key) {
        window.open(`/app/buyer#plebeian-auction-${key}`, '_blank');
    }

    function startAuction(key) {
        // TODO
    }

    onMount(async () => { fetchAPI("/auctions", 'GET', $token, null, checkResponse); });
</script>

<style>
    .invalid {
        color: #991B1B;
    }
    .invalid-field {
        border-bottom: 2px solid #991B1B;
    }
</style>

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
    {:else if currentAuction}
        <div class="w-full flex justify-center items-center">
            <div class="w-4/6 p-4 rounded shadow-lg bg-gray-900 my-3 glowbox">
                <h3 class="mb-4 text-2xl text-center text-white">{#if isEdit}Edit auction <code class="bg-cyan-600 p-1 rounded">{currentAuction.key}</code>{:else}Create a new auction{/if}</h3>
                <form>
                    <div class="flex">
                    <div class="form-group mr-2 w-full">
                        <input class="form-field" class:invalid-field={currentAuction.invalidTitle && currentAuction.title.length === 0} name="title" bind:value={currentAuction.title} type="text" id="title" />
                        <label class="form-label" class:invalid={currentAuction.invalidTitle && currentAuction.title.length === 0} for="title">Title *</label>
                    </div>
                    </div>
                    <div class="flex">
                    <div class="form-group mr-2 w-full">
                        <textarea class="form-field" class:invalid-field={currentAuction.invalidDescription && currentAuction.description.length === 0} name="description" bind:value={currentAuction.description} id="description"></textarea>
                        <label class="form-label" class:invalid={currentAuction.invalidDescription && currentAuction.description.length === 0} for="reserve-bid">Description *</label>
                    </div>
                    </div>
                    <div class="flex">
                        <div class="form-group mr-2 w-1/2">
                            <input class="form-field" name="starting-bid" bind:value={currentAuction.starting_bid} type="number" id="starting-bid" />
                            <label class="form-label" for="starting-bid">Starting bid</label>
                        </div>
                        <div class="form-group ml-2 w-1/2">
                            <input class="form-field" name="reserve-bid" bind:value={currentAuction.reserve_bid} type="number" id="reserve-bid" />
                            <label class="form-label" for="reserve-bid">Reserve bid</label>
                        </div>
                    </div>
                    <div class="form-group mr-2 w-full">
                        <input type="hidden" name="duration-hours" bind:value={currentAuction.duration_hours} />
                        <div class="flex justify-center items-center">
                            <div class="w-1/3 mt-5 text-center">
                                <span class="text-indigo-200 mr-2 mt-5 p-2">Duration</span>
                            </div>
                            <div class="w-2/3 mt-5 flex justify-center items-center">
                                <button class:bg-black={currentAuction.duration_hours === 1} class="mr-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black float-left hidden md:inline-block" on:click|preventDefault={() => currentAuction.duration_hours = 1}>An hour</button>
                                <button class:bg-black={currentAuction.duration_hours === 24} class="mr-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black float-left hidden md:inline-block" on:click|preventDefault={() => currentAuction.duration_hours = 24}>A day</button>
                                <button class:bg-black={currentAuction.duration_hours === 24 * 7} class="mr-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black float-left hidden md:inline-block" on:click|preventDefault={() => currentAuction.duration_hours = 24 * 7}>A week</button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>
        <div class="w-full flex justify-center items-center">
            <div class="w-4/6">
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
            </div>
        </div>
    {:else}
        <div class="flex items-center justify-center">
            <div class="glowbutton glowbutton-create" on:click|preventDefault={startCreate}></div>
        </div>
        {#each auctions as auction}
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
                    <div class="glowbutton glowbutton-copy" on:click|preventDefault={copyAuction(auction.key)}></div>
                </div>
                <div class="float-right pt-5">
                    <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black" on:click={viewAuction(auction.key)}>View</button>
                    {#if !auction.started}
                        <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-green-800" on:click={startAuction(auction.key)}>Start</button>
                        {#if !auction.canceled}
                            <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-black" on:click={startEdit(auction)}>Edit</button>
                        {/if}
                        <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-red-800" on:click={deleteAuction(auction.key)}>Delete</button>
                    {/if}
                    {#if !auction.canceled && !auction.ended}
                        <button class="m-2 p-2 border-2 rounded text-indigo-200 border-pink-300 hover:bg-red-800" on:click={cancelAuction(auction.key)}>Cancel</button>
                    {/if}
                </div>
            </div>
        {/each}
    {/if}
</section>
</div>