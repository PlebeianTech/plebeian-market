<script lang="ts">
    import { onMount } from 'svelte';
    import SvelteMarkdown from 'svelte-markdown';
    import { ErrorHandler, deleteEntity, hideAuction } from "$lib/services/api";
    import { Error, Info, token, user } from "$lib/stores";
    import type { IEntity } from "$lib/types/base";
    import { Auction } from "$lib/types/auction";
    import { Listing } from "$lib/types/listing";
    import type { Item } from "$lib/types/item";
    import AmountFormatter, { AmountFormat } from "$lib/components/AmountFormatter.svelte";
    import Avatar from "$lib/components/Avatar.svelte";
    import Countdown, { CountdownStyle } from "$lib/components/Countdown.svelte";

    export let isEditable = false;
    export let showCampaign = false;
    export let showOwner = false;

    export let entity: IEntity;
    $: item = <Item>(<unknown>entity);

    $: url = `/${item.endpoint}/${item.key}`;
    $: topBid = (item instanceof Auction) ? item.topBid() : null;

    let box; // the whole box representing this item (the HTML Element)

    export let onEdit = (_: Item) => {};
    export let onEntityChanged = () => {};

    function hide() {
        hideAuction($token, item.key,
            () => {
                Info.set("Hidden from homepage.");
            },
            new ErrorHandler(false, () => Error.set("Failed to hide the item.")));
    }

    function del() {
        if (window.confirm("Are you sure?")) {
            deleteEntity($token, entity, onEntityChanged);
        }
    }

    onMount(async () => {
        if (item && window.location.hash === `#item-${item.key}`) {
            window.scrollTo(0, box.offsetTop);
        }
    });
</script>

<div bind:this={box} class="group">
    <div class="flex flex-row-reverse gap-2 invisible group-hover:visible">
        <div class="btn-xs"></div>
        {#if isEditable}
            {#if item instanceof Listing || (item instanceof Auction && item.editable_for_seconds && item.bids.length === 0)}
                <button class="btn btn-primary btn-circle btn-xs" on:click={del}>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" width="512.000000pt" height="512.000000pt" viewBox="0 0 512 512" stroke="currentColor">
                        <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)" fill="#000000" stroke="none">
                            <path d="M1871 5109 c-128 -25 -257 -125 -311 -241 -37 -79 -50 -146 -50 -259 l0 -89 -389 0 c-222 0 -411 -4 -442 -10 -187 -36 -330 -184 -361 -376 -30 -181 66 -371 231 -458 l69 -36 6 -58 c4 -31 65 -763 136 -1627 72 -863 134 -1587 139 -1608 36 -155 177 -295 335 -332 91 -22 2561 -22 2652 0 158 37 299 177 335 332 5 21 67 745 139 1608 71 864 132 1596 136 1627 l6 58 69 36 c165 87 261 277 231 458 -31 192 -174 340 -361 376 -31 6 -220 10 -442 10 l-389 0 0 89 c0 48 -5 112 -10 142 -34 180 -179 325 -359 359 -66 12 -1306 12 -1370 -1z m1359 -309 c60 -31 80 -78 80 -190 l0 -90 -750 0 -750 0 0 90 c0 110 20 159 78 189 36 19 60 20 670 21 615 0 634 -1 672 -20z m1200 -600 c45 -23 80 -80 80 -130 0 -50 -35 -107 -80 -130 -39 -20 -55 -20 -1870 -20 -1815 0 -1831 0 -1870 20 -45 23 -80 80 -80 130 0 48 35 107 78 129 36 20 65 20 1870 21 1818 0 1833 0 1872 -20z m-236 -622 c-2 -24 -63 -747 -134 -1606 -140 -1694 -129 -1598 -193 -1646 l-28 -21 -1279 0 -1279 0 -28 21 c-64 48 -53 -48 -193 1646 -71 859 -132 1582 -134 1606 l-6 42 1640 0 1640 0 -6 -42z"/>
                            <path d="M1587 3299 c-25 -13 -45 -34 -58 -62 l-21 -43 76 -1234 c85 -1381 76 -1299 155 -1340 51 -25 91 -25 142 0 27 14 46 34 60 63 l21 43 -76 1234 c-85 1381 -76 1299 -155 1340 -50 25 -95 25 -144 -1z"/>
                            <path d="M2488 3299 c-23 -12 -46 -35 -58 -59 -20 -39 -20 -57 -20 -1280 0 -1224 0 -1241 20 -1280 23 -45 80 -80 130 -80 50 0 107 35 130 80 20 39 20 56 20 1280 0 1224 0 1241 -20 1280 -37 73 -127 99 -202 59z"/>
                            <path d="M3387 3299 c-77 -41 -68 37 -153 -1339 l-76 -1234 21 -43 c14 -29 33 -49 60 -63 51 -25 91 -25 142 0 79 41 70 -41 155 1340 l76 1234 -21 43 c-37 75 -127 103 -204 62z"/>
                        </g>
                    </svg>
                </button>
                <button class="btn btn-primary btn-circle btn-xs" on:click={() => onEdit(item)}>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" width="512.000000pt" height="512.000000pt" viewBox="0 0 512 512" stroke="currentColor">
                        <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)" fill="#000000" stroke="none">
                            <path d="M3861 5110 c-57 -12 -157 -60 -201 -96 -55 -45 -3166 -3188 -3178 -3211 -17 -30 -482 -1665 -482 -1691 0 -53 62 -112 117 -112 10 0 394 108 852 239 l834 240 136 134 c399 393 2734 2707 2897 2871 243 243 279 305 279 476 0 89 -17 155 -58 230 -37 69 -787 823 -858 864 -25 14 -68 33 -95 41 -62 19 -186 27 -243 15z m187 -245 c47 -20 784 -752 814 -810 29 -55 29 -145 0 -200 -11 -22 -139 -158 -286 -305 l-266 -265 -512 513 -513 512 265 266 c170 170 279 273 305 285 49 23 142 25 193 4z m-710 -938 l212 -212 -1119 -1119 -1119 -1119 -85 169 c-47 93 -95 178 -107 189 -19 17 -39 21 -137 23 -63 2 -113 7 -111 12 4 9 2241 2268 2248 2269 3 1 101 -95 218 -212z m800 -807 c-5 -10 -2260 -2245 -2268 -2248 -5 -2 -10 48 -12 111 -2 98 -6 118 -23 137 -11 12 -96 60 -189 107 l-169 85 1119 1119 1119 1119 212 -212 c117 -117 212 -215 211 -218z m-3053 -1708 l110 -217 217 -110 218 -110 0 -152 0 -152 -52 -16 c-29 -8 -154 -44 -278 -80 l-225 -64 -282 282 -282 282 64 225 c36 124 72 249 80 278 l16 52 152 0 152 0 110 -218z m-455 -787 c101 -101 182 -186 180 -188 -10 -8 -513 -148 -517 -144 -5 6 140 517 147 517 3 0 88 -83 190 -185z" />
                        </g>
                    </svg>            
                </button>
                {#if item instanceof Auction && item.editable_for_seconds && item.bids.length === 0}
                    <Countdown totalSeconds={item.editable_for_seconds} style={CountdownStyle.Compact} />
                    <span>editable for</span>
                {/if}
            {/if}
        {/if}
    </div>
    <div class="card bg-base-300 max-w-full overflow-hidden shadow-xl my-3 mx-3">
        <a href={url}>
            <figure class="h-full flex justify-center">
                {#each item.media as photo, i}
                    {#if i === 0}
                        <img class="object-contain" src={photo.url} alt="Item" />
                    {/if}
                {/each}
            </figure>
        </a>
        <div class="card-body w-full">
          <div class="mb-8">
            <h2 class="card-title mb-2">
                <a href={url}>{item.title}</a>
            </h2>
            <div class="markdown-container max-h-52 overflow-hidden">
                <SvelteMarkdown source={item.description} />
            </div>
          </div>
          <div class="flex space-x-2 items-center">
            
              {#if showCampaign && item.campaign_name !== null}
                  <div class="badge badge-primary"><a href="/campaigns/{item.campaign_key}"><nobr>{item.campaign_name} campaign</nobr></a></div>
              {/if}

              {#if item instanceof Auction}
                  <div class="badge badge-secondary">auction</div>
              {:else if item instanceof Listing}
                  <div class="badge badge-secondary">fixed price</div>
              {/if}
         
 
              {#if item instanceof Auction}
                  {#if item.started && !item.ended}
                      <Countdown totalSeconds={item.ends_in_seconds} style={CountdownStyle.Compact} />
                  {:else if item.ended}
                      <div class="badge badge-primary">ended</div>
                  {/if}
              {:else if item instanceof Listing}
                  {#if item.available_quantity === 0}
                      <div class="badge badge-primary">sold out</div>
                  {/if}
              {/if}
            </div>
            <p class="lg:text-3xl text-2xl">
                {#if item instanceof Auction}
                    {#if item.has_winner && item.winner}
                        Winner: <a rel="external" class="link" href="/stall/{item.winner.nym}">{item.winner.nym}</a>
                        <br />
                        Amount: <AmountFormatter satsAmount={item.topAmount()} />
                    {:else if item.bids.length !== 0}
                        Bids: {item.bids.length}
                        <br />
                        {#if topBid && topBid.buyer}
                            Top bid: <AmountFormatter satsAmount={topBid.amount} format={AmountFormat.Sats} />
                            <br />
                            Bidder: <a rel="external" class="link" href="/stall/{topBid.buyer.nym}">{topBid.buyer.nym}</a>
                        {/if}
                    {:else if !item.ended}
                        Starting bid: <AmountFormatter satsAmount={item.starting_bid} format={AmountFormat.Sats} />
                    {/if}
                {:else if item instanceof Listing}
                    Price: ${item.price_usd}
                    <br />
                    ~<AmountFormatter usdAmount={item.price_usd} format={AmountFormat.Sats} />
                    <br />
                    <span>Stock: {item.available_quantity}</span>
                {/if}
            </p>
            {#if showOwner}
                <div class="divider"></div>
                <div class="flex items-center justify-center gap-2">
                    <span>by</span>
                    <Avatar account={item.seller} inline={true} />
                </div>
            {/if}
            
            {#if $user && $user.isModerator}
                <div class="btn self-center md:float-right" on:click|preventDefault={hide} on:keypress={hide}>Hide from homepage</div>
            {/if}
        </div>
    </div>
</div>
