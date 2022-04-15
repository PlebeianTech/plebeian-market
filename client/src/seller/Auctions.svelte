<script>
    import { onMount } from 'svelte';
    import dayjs from 'dayjs';
    import Time from 'svelte-time';
    import { token, fromJson, fetchAPI } from "../common.js";

    function emptyAuction() {
        return {
            minimum_bid: 10000,
            starts_at: dayjs(new Date()).startOf('day').add(1, 'day').format("YYYY-MM-DDTHH:mm"),
            ends_at: dayjs(new Date()).startOf('day').add(2, 'days').format("YYYY-MM-DDTHH:mm")
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
            if (k === 'starts_at' || k === 'ends_at') {
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
        const snippet = '<link rel="stylesheet" href="https://plebeian.market/static/css/common.css">'
            + `<div id="plebeian-auction" data-key="${key}"></div>`
            + '<script src="https://plebeian.market/app/buyer/bundle.js">'+ "</" + "script>";
        navigator.clipboard.writeText(snippet).then(() => alert("Snippet copied!"));
    }

    function openAuction(key) {
        window.open(`/app/buyer#plebeian-auction-${key}`, '_blank');
    }

    onMount(async () => { fetchAPI("/auctions", 'GET', $token, null, checkResponse); });
</script>

<style>
    .left {
        float: left;
    }
    .right {
        float: right;
    }
    .modal {
        display: block;
    }
</style>

<section>
    <div class="container">
        {#if confirmation}
        <div class="modal" id="confirmation" tabindex="-1" role="dialog">
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">{confirmation.message}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close" on:click={confirmation.close}>
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <input type="text" bind:value={confirmation.input} />
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal" on:click={confirmation.close}>Close</button>
                        <button type="button" class="btn btn-primary" on:click={confirmation.continue}>Continue</button>
                    </div>
                </div>
            </div>
        </div>
        {:else if auction}
        <div class="row mt-5">
            <div class="col-md-12">
                <div class="card p-2 glow-box">
                    <div class="card-body">
                        <h3 class="card-title mb-4">{#if isEdit}Edit auction {auction.key}{:else}Create a new auction{/if}</h3>
                        <form id="new-auction">
                            <div class="form-group">
                                <input class="form-field" type="datetime-local" name="starts-at" bind:value={auction.starts_at} />
                                <label class="form-label" for="starts-at">Starts</label>
                            </div>
                            <div class="form-group">
                                <input class="form-field" type="datetime-local" name="ends-at" bind:value={auction.ends_at} />
                                <label class="form-label" for="ends-at">Ends</label>
                            </div>
                            <div class="form-group">
                                <input class="form-field" name="minimum-bid" bind:value={auction.minimum_bid} type="number" id="minimum-bid" />
                                <label class="form-label" for="minimum-bid">Minimum bid</label>
                            </div>
                            <div class="left">
                                {#if isEdit}
                                    <div class="glowbutton glowbutton-save" on:click|preventDefault={updateAuction}></div>
                                {:else}
                                    <div class="glowbutton glowbutton-save" on:click|preventDefault={createAuction}></div>
                                {/if}                                
                            </div>
                            <div class="right">
                                <button class="btn-white" on:click|preventDefault={cancelEdit}>Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        {:else}
        <div class="glowbutton glowbutton-create" on:click|preventDefault={startCreate}></div>
        <div class="row mt-3">
            <div class="col-md-12">
                {#each auctions as a}
                <div class="card mb-2">
                    <div class="card-body">
                        <p class="card-text text-center"><code>{ a.key }</code> {#if a.ended}<span>(ended)</span>{:else if a.canceled}<span>(canceled)</span>{/if}</p>
                        <p class="card-text">From <Time timestamp={ a.starts_at } format="dddd MMMM D, H:mm" /> - <Time timestamp={ a.ends_at } format="dddd MMMM D, H:mm - YYYY" /></p>
                        <p class="card-text"><span>Minimum bid: { a.minimum_bid }</span><span class="right">Bids: { a.bids.length }</span></p>
                        <div class="left">
                            <div class="glowbutton glowbutton-copy" on:click|preventDefault={copyAuction(a.key)}></div>
                        </div>
                        <div class="right">
                            <button class="btn-white" on:click={openAuction(a.key)}>Open</button>
                            {#if !a.started}
                                {#if !a.canceled}
                                    <button class="btn-white" on:click={startEdit(a)}>Edit</button>
                                {/if}
                                <button class="btn-white" on:click={deleteAuction(a.key)}>Delete</button>
                            {/if}
                            {#if !a.canceled && !a.ended}
                                <button class="btn-white" on:click={cancelAuction(a.key)}>Cancel</button>
                            {/if}
                        </div>
                    </div>
                </div>
                {/each}
            </div>
        </div>
        {/if}
    </div>
</section>