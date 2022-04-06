<script>
    import { onMount } from 'svelte';
    import { DateInput } from 'date-picker-svelte';
    import Time from 'svelte-time';

    let auctions = [];

    function emptyAuction() {
        var defaultStartsAt = new Date();
        defaultStartsAt.setHours(24, 0, 0, 0); // next midnight
        var defaultEndsAt = new Date();
        defaultEndsAt.setHours(48, 0, 0, 0); // 1 day after

        return { minimum_bid: 10000, starts_at: defaultStartsAt, ends_at: defaultEndsAt };
    }

    let data = emptyAuction();

    function createAuction () {
        var formBody = [];
        for (var property in data) {
            var encodedKey = encodeURIComponent(property);
            var encodedValue = encodeURIComponent((data[property] instanceof Date) ? data[property].toISOString() : data[property]);
            formBody.push(encodedKey + "=" + encodedValue);
        };
        doPost("/api/auctions", formBody.join("&"),
            (response) => {
                if (response.success) {
                    refreshAuctions();
                }
            },
            (response) => { alert(`Error: ${response.message}`); }
        );
        data = emptyAuction();
    };

    function deleteAuction(key) {
        doDelete(`/api/auctions/${key}`,
            (response) => {
                if (response.success) {
                    refreshAuctions();
                }
            },
            (response) => { alert(`Error: ${response.message}`); }
        );
    }

    function refreshAuctions() {
        doGet("/api/auctions",
            (response) => {
                auctions = response.auctions;
        });
    }

    onMount(async () => {
        refreshAuctions();
    });
</script>

<section>
    <div class="container">
        <div class="row mt-5">
            <div class="col-md-6">
                <div class="card p-2 shadow">
                    <div class="card-body">
                        <h5 class="card-title mb-4">Create a new Auction</h5>
                        <form id="new-auction">
                            <div class="form-group">
                                <label for="minimum-bid">Minimum bid</label>
                                <input bind:value={data.minimum_bid} type="number" class="form-control" id="minimum-bid" />
                            </div>
                            <div class="form-group">
                                <label for="starts-at">Starts at</label>
                                <DateInput bind:value={data.starts_at} format="yyyy/MM/dd HH:mm:ss" />
                            </div>
                            <div class="form-group">
                                <label for="ends-at">Ends at</label>
                                <DateInput bind:value={data.ends_at} format="yyyy/MM/dd HH:mm:ss" />
                            </div>
                            <button type="submit" class="btn btn-primary" on:click|preventDefault={createAuction}>Create</button>
                        </form>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                {#each auctions as auction }
                <div class="card">
                    <div class="card-header">Auction { auction.key }</div>
                    <div class="card-body">
                        <p class="card-text">Starts at: <Time timestamp={auction.starts_at} format="dddd @ H:mm UTC · MMMM D, YYYY" /></p>
                        <p class="card-text">Ends at: <Time timestamp={auction.ends_at} format="dddd @ H:mm UTC · MMMM D, YYYY" /></p>
                        <p class="card-text">Minimum bid: { auction.minimum_bid }</p>
                        <p class="card-text">Bids: { auction.bids.length }</p>
                        <button class="btn btn-danger" on:click|preventDefault={deleteAuction(auction.key)}>Delete</button>
                    </div>
                </div>
                {/each}
            </div>
        </div>
    </div>
</section>