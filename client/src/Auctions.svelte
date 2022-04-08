<script>
    import { onMount } from 'svelte';
    import { DateInput } from 'date-picker-svelte';
    import Time from 'svelte-time';
    import { token } from "./stores.js";

    function emptyAuction() {
        var defaultStartsAt = new Date();
        defaultStartsAt.setHours(24, 0, 0, 0); // next midnight
        var defaultEndsAt = new Date();
        defaultEndsAt.setHours(48, 0, 0, 0); // 1 day after

        return { minimum_bid: 10000, starts_at: defaultStartsAt, ends_at: defaultEndsAt };
    }

    let auction = emptyAuction();
    let isEdit = false;
    let auctions = [];

    function asJson() {
        var json = {};
        for (var k in auction) {
            json[k] = (auction[k] instanceof Date) ? auction[k].toISOString() : auction[k];
        }
        return JSON.stringify(json);
    }

    function fromJson(json) {
        var a = {};
        for (var k in json) {
            a[k] = (k === 'starts_at' || k === 'ends_at' ? new Date(json[k]) : json[k]);
        }
        return a;
    }

    function checkResponse(response) {
        if (response.status === 200) {
            auction = emptyAuction();
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
                return response.json().then(data => { console.log(`Error ${response.status}: ${data.message}`); });
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
        fetchAPI(`/auctions/${key}`, 'DELETE');
    }

    function updateAuction () {
        isEdit = false;

        fetchAPI(`/auctions/${auction.key}`, 'PUT', asJson());
    }

    function startEdit(a) {
        isEdit = true;
        auction = a;
    }

    function cancelEdit() {
        isEdit = false;
        auction = emptyAuction();
    }

    onMount(async () => { fetchAPI("/auctions", 'GET'); });
</script>

<section>
    <div class="container">
        <div class="row mt-5">
            <div class="col-md-6">
                <div class="card p-2 glow-box">
                    <div class="card-body">
                        <h5 class="card-title mb-4">{#if isEdit}Edit auction {auction.key}{:else}Create a new auction{/if}</h5>
                        <form id="new-auction">
                            <div class="form-group">
                                <label for="minimum-bid">Minimum bid</label>
                                <input bind:value={auction.minimum_bid} type="number" class="form-control" id="minimum-bid" />
                            </div>
                            <div class="form-group">
                                <label for="starts-at">Starts</label>
                                <DateInput bind:value={auction.starts_at} format="yyyy/MM/dd HH:mm:ss" />
                            </div>
                            <div class="form-group">
                                <label for="ends-at">Ends</label>
                                <DateInput bind:value={auction.ends_at} format="yyyy/MM/dd HH:mm:ss" />
                            </div>
                            {#if isEdit}
                                <button type="submit" class="btn btn-primary" on:click|preventDefault={updateAuction}>Save</button>
                                <button class="btn btn-info" on:click|preventDefault={cancelEdit}>Cancel edit</button>
                            {:else}
                                <button type="submit" class="btn btn-primary" on:click|preventDefault={createAuction}>Create</button>
                            {/if}
                        </form>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                {#each auctions as a }
                <div class="card">
                    <div class="card-body">
                        <p class="card-text">ID: { a.key }</p>
                        <p class="card-text">Starts: <Time timestamp={a.starts_at} format="dddd @ H:mm UTC · MMMM D, YYYY" /></p>
                        <p class="card-text">Ends: <Time timestamp={a.ends_at} format="dddd @ H:mm UTC · MMMM D, YYYY" /></p>
                        <p class="card-text">Minimum bid: { a.minimum_bid }</p>
                        <p class="card-text">Bids: { a.bids.length }</p>
                        <button class="btn btn-info" on:click={startEdit(a)}>Edit</button>
                        <button class="btn btn-danger" on:click={deleteAuction(a.key)}>Delete</button>
                    </div>
                </div>
                {/each}
            </div>
        </div>
    </div>
</section>