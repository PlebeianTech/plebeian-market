<script>
    import { onMount } from 'svelte';
    import { toasts, ToastContainer }  from "svelte-toasts";
    import { fromJson, fetchAPI } from "./common.js";
    import { token } from "./stores.js";
    import AuctionCard from "./AuctionCard.svelte";
    import AuctionEditor from "./AuctionEditor.svelte";
    import Confirmation from "./Confirmation.svelte";
    import Loading from "./Loading.svelte";

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
    let auctions = null;

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
                        currentAuction = emptyAuction();
                    }
                } else {
                    fetchAPI("/auctions", 'GET', $token, null, checkResponse);
                }
            });
        } else {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.indexOf('application/json') !== -1) {
                return response.json().then(data => { alert(`Error: ${data.message}`); });
            } else {
                return response.text().then(text => { console.log(`Error ${response.status}: ${text}`); });
            }
        }
    }

    function saveCurrentAuction() {
        currentAuction.invalidTitle = currentAuction.title.length === 0;
        currentAuction.invalidDescription = currentAuction.description.length === 0;
        if (currentAuction.invalidTitle || currentAuction.invalidDescription) {
            return;
        }

        if (currentAuction.key) {
            fetchAPI(`/auctions/${currentAuction.key}`, 'PUT', $token, asJson(), checkResponse);
        } else {
            fetchAPI("/auctions", 'POST', $token, asJson(), checkResponse);
            const toast = toasts.add({
                title: "Auction created",
                description: "Your auction will start when we verify your tweet",
                duration: 3000,
                placement: 'bottom-right',
                type: 'info'
            });
        }
    }

    function deleteAuction(key) {
        confirmation = {
            message: "Type DELETE MY AUCTION below to continue...",
            expectedInput: "DELETE MY AUCTION",
            onContinue: () => { fetchAPI(`/auctions/${key}`, 'DELETE', $token, null, checkResponse); }
        };
    }

    function cancelAuction(key) {
        confirmation = {
            message: "Type CANCEL MY AUCTION below to continue...",
            expectedInput: "CANCEL MY AUCTION",
            onContinue: () => { fetchAPI(`/auctions/${key}`, 'PUT', $token, JSON.stringify({'canceled': true}), checkResponse); }
        };
    }

    onMount(async () => { fetchAPI("/auctions", 'GET', $token, null, checkResponse); });
</script>

<div class="pt-10 flex justify-center items-center">
    <section class="w-3/5">
        {#if confirmation}
            <Confirmation message={confirmation.message} expectedInput={confirmation.expectedInput} onContinue={confirmation.onContinue} onCancel={() => confirmation = null} />
        {:else if currentAuction}
            <AuctionEditor bind:auction={currentAuction} onSave={saveCurrentAuction} />
        {:else if auctions == null}
            <Loading />
        {:else}
            <div class="flex items-center justify-center">
                <div class="glowbutton glowbutton-create" on:click|preventDefault={() => currentAuction = emptyAuction()}></div>
            </div>
            {#each auctions as auction}
                <AuctionCard auction={auction} onEdit={(auction) => currentAuction = auction} onCancel={cancelAuction} onDelete={deleteAuction} />
            {/each}
        {/if}
    </section>
    <ToastContainer placement="bottom-right" let:data={data}>
        <div class="alert alert-info shadow-lg">
            <div>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              <span>{data.description}</span>
            </div>
          </div>
    </ToastContainer>
</div>