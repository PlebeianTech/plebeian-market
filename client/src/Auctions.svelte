<script>
    import { onMount } from 'svelte';
    import dayjs from 'dayjs';
    import Time from 'svelte-time';
    import { token } from "./stores.js";

    function emptyAuction() {
        return {
            minimum_bid: 10000,
            starts_at: dayjs(new Date()).startOf('day').add(1, 'day').format("YYYY-MM-DDTHH:mm"),
            ends_at: dayjs(new Date()).startOf('day').add(2, 'days').format("YYYY-MM-DDTHH:mm")
        };
    }

    let auction = null;
    let isEdit = false;
    let auctions = [];

    function asJson() {
        var json = {};
        for (var k in auction) {
            if (k === 'starts_at' || k === 'ends_at') {
                json[k] = dayjs(auction[k]).toISOString();
            } else {
                json[k] = auction[k];
            }
        }
        return JSON.stringify(json);
    }

    function fromJson(json) {
        var a = {};
        for (var k in json) {
            if (k === 'starts_at' || k === 'ends_at') {
                a[k] = dayjs(new Date(json[k])).format("YYYY-MM-DDTHH:mm");
            } else {
                a[k] = json[k];
            }
        }
        return a;
    }

    function checkResponse(response) {
        if (response.status === 200) {
            auction = null;
            response.json().then(data => {
                if (data.auctions) {
                    auctions = data.auctions.map(fromJson);
                } else {
                    fetchAPI("/auctions", 'GET');
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

    function fetchAPI(path, method, json) {
        var API_BASE = "/api";
        var headers = {};
        if ($token) {
            headers['X-Access-Token'] = $token;
        }
        if (json) {
            headers['Content-Type'] = 'application/json';
        }
        var fetchOptions = {method, headers};
        if (json) {
            fetchOptions['body'] = json;
        }
        fetch(`${API_BASE}${path}`, fetchOptions).then(checkResponse);
    }

    function createAuction() {
        fetchAPI("/auctions", 'POST', asJson());
    }

    function deleteAuction(key) {
        if (confirm("Are you sure?")) {
            fetchAPI(`/auctions/${key}`, 'DELETE');
        }
    }

    function updateAuction () {
        fetchAPI(`/auctions/${auction.key}`, 'PUT', asJson());
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

    function copyAuction() {
        
    }

    function openAuction(key) {
        window.open(`/app/auction#${key}`, '_blank');
    }

    onMount(async () => { fetchAPI("/auctions", 'GET'); });
</script>

<style>
    .left {
        float: left;
    }
    .right {
        float: right;
    }
</style>

<section>
    <div class="container">
        {#if auction}
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
                {#each auctions as a }
                <div class="card mb-2">
                    <div class="card-body">
                        <p class="card-text text-center"><code>{ a.key }</code></p>
                        <p class="card-text">From <Time timestamp={a.starts_at} format="dddd @ H:mm · MMMM D, YYYY" /> to <Time timestamp={a.ends_at} format="dddd @ H:mm · MMMM D, YYYY" /></p>
                        <p class="card-text"><span>Minimum bid: { a.minimum_bid }</span><span class="right">Bids: { a.bids.length }</span></p>
                        <div class="left">
                            <div class="glowbutton glowbutton-copy" on:click|preventDefault={copyAuction}></div>
                        </div>
                        <div class="right">
                            <button class="btn-white" on:click={openAuction(a.key)}>Open</button>
                            <button class="btn-white" on:click={startEdit(a)}>Edit</button>
                            <button class="btn-white" on:click={deleteAuction(a.key)}>Delete</button>
                        </div>
                    </div>
                </div>
                {/each}
            </div>
        </div>
        {/if}
    </div>
</section>