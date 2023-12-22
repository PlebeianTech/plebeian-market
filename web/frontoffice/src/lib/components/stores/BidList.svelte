<script lang="ts">
    import { fade } from 'svelte/transition';
    import {formatTimestamp} from "$sharedLib/nostr/utils";
    import profilePicturePlaceHolder from "$sharedLib/images/profile_picture_placeholder.svg";
    import Clock from "$sharedLib/components/icons/Clock.svelte";
    import WinnerBadge from "$sharedLib/components/icons/WinnerBadge.svelte";
    import Nip05Checkmark from "$lib/components/nostr/Nip05Checkmark.svelte";
    import UserInfoPopup from "$sharedLib/components/nostr/UserInfoPopup.svelte";
    import {NostrPublicKey} from "$sharedLib/stores";
    import {nip19} from "nostr-tools";
    import {onImgError} from "$lib/shopping";
    import CurrencyConverter from "$sharedLib/components/CurrencyConverter.svelte";

    export let sortedBids;
    export let userProfileInfoMap;
    export let openSitgBadgeInfo;
    export let bidSuscriptionFinished = false;

    let modalPubkey = null;
    let hoverTimer = null;
    let mobile = false;

    const winnerColor = 'bg-green-300 dark:bg-[#446600]';

    async function showUserProfilePopup(event, pubkey) {
        mobile = !event;

        modalPubkey = pubkey;

        if (mobile) {
            window.user_information_modal.showModal();
        } else {
            const userInfoPopup = document.getElementById('user-information-popup');

            if (userInfoPopup) {
                const mouseX = event.pageX;
                const mouseY = event.pageY;

                const popupWidth = userInfoPopup.offsetWidth;
                const popupHeight = userInfoPopup.offsetHeight;

                if (event.clientY <= (window.innerHeight / 2)) {
                    userInfoPopup.style.left = `${mouseX - (popupWidth / 2)}px`;
                    userInfoPopup.style.top = `${mouseY + 10}px`;
                } else {
                    userInfoPopup.style.left = `${mouseX - (popupWidth / 2)}px`;
                    userInfoPopup.style.top = `${mouseY - popupHeight - 40}px`;
                }
            }
        }

    }

    function hideUserProfilePopup() {
        if (!mobile) {
            if (hoverTimer) {
                window.clearTimeout(hoverTimer);
            }
        } else {
            window.user_information_modal.close();
        }

        modalPubkey = null;
    }
</script>

{#if sortedBids && sortedBids.length > 0}
    <div class="mt-8 mb-6">
        <!-- Mobile -->
        <table class="md:hidden w-full table table-fixed table-sm sm:table-md md:table-lg text-center">
            <thead>
                <tr class="text-lg">
                    <th class="pl-0">Bid</th>
                    <th class="pr-0">Info</th>
                </tr>
            </thead>
            <tbody>
            {#each sortedBids as [_, bid]}
                {#if bid.amount}
                    <tr class:bg-success={bid.backendResponse && bid.backendResponse.status === 'winner'}>
                        <th class="text-center grid {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">
                            {#if bidSuscriptionFinished}
                                <CurrencyConverter
                                    amount={bid.amount}
                                    sourceCurrency="sats"
                                    satsClassStyle="text-xs pb-1"
                                />
                            {/if}
                            <p class="mt-1">{formatTimestamp(bid.date)}</p>

                            <div class="mt-1">
                                {#if !bid.backendResponse}
                                    <div class="mx-auto tooltip" data-tip="Waiting response from marketplace">
                                        <div class="w-8 h-8 mx-auto"><Clock /></div>
                                    </div>
                                {:else if bid.backendResponse.status === 'accepted'}
                                    <div class="mx-auto tooltip tooltip-right" data-tip="Bid confirmed">✅</div>
                                {:else if bid.backendResponse.status === 'rejected'}
                                    <div class="mx-auto tooltip tooltip-right" data-tip="Bid rejected: {bid.backendResponse.message}">❌</div>
                                {:else if bid.backendResponse.status === 'pending'}
                                    <div class="w-8 h-8 mx-auto tooltip tooltip-right" data-tip={ bid.backendResponse.badge_stall_id ? "Bid pending: Skin in the Game required" : "Bid pending: " + bid.backendResponse.message }><Clock /></div>
                                    {#if bid.pubkey === $NostrPublicKey}
                                        <p class="line-clamp-3 mt-1 whitespace-normal">
                                            <button class="btn btn-sm btn-success" on:click|preventDefault={() => openSitgBadgeInfo(bid.backendResponse.badge_stall_id, bid.backendResponse.badge_product_id, true)}>Skin in the Game required</button>
                                        </p>
                                    {/if}
                                {:else if bid.backendResponse.status === 'winner'}
                                    <div class="mx-auto tooltip tooltip-right" data-tip="{bid.backendResponse.winnerPubkey === $NostrPublicKey ? 'Congratulations!' : 'This is the winning bid'}"><div class="w-8 h-8 mx-auto"><WinnerBadge /></div></div>
                                {:else}
                                    Unknown response from the marketplace
                                {/if}
                            </div>
                        </th>
                        <th class="{bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}r">
                            <div class="flex w-fit mx-auto mt-1 space-x-3 items-center" on:click={() => {showUserProfilePopup(null, bid.pubkey)}}>
                                <div class="avatar mask mask-squircle w-12 h-12">
                                    <img
                                            src={userProfileInfoMap.get(bid.pubkey)?.picture ?? profilePicturePlaceHolder}
                                            on:error={(event) => onImgError(event.srcElement, profilePicturePlaceHolder)}>
                                            alt="Avatar of the identity that made the bid"
                                    />
                                </div>
                                <div class="flex">
                                    <span>{userProfileInfoMap.get(bid.pubkey)?.name?.substring(0,15) ?? bid.pubkey.substring(0,9) + '...'}</span>
                                    {#if userProfileInfoMap.get(bid.pubkey)?.nip05VerifiedAddress}
                                        <span class="ml-1">
                                            <Nip05Checkmark address="{userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}" />
                                        </span>
                                    {/if}
                                </div>
                            </div>
                        </th>
                    </tr>
                {/if}
            {/each}
            </tbody>
        </table>

        <!-- Desktop -->
        <table class="hidden md:block table table-lg table-fixed w-max text-center">
            <thead>
                <tr class="text-sm">
                    <th>Bid</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>
                        Bidder
                        <p class="text-[10px]">(hover profile pictures with the mouse)</p>
                    </th>
                </tr>
            </thead>
            <tbody>

            {#each sortedBids as [_, bid]}
                {#if bid.amount}
                    <tr>
                        <th class="text-center inline-grid {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">
                            <span class="p-3" class:pb-9={!bidSuscriptionFinished}>
                                {#if bidSuscriptionFinished}
                                    <div class="pt-1">
                                        <CurrencyConverter
                                            amount={bid.amount}
                                            sourceCurrency="sats"
                                        />
                                    </div>
                                {/if}
                            </span>
                        </th>
                        <td class="text-center {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">{formatTimestamp(bid.date)}</td>
                        <td class="text-center text-xs {bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor : ''}">
                            {#if !bid.backendResponse}
                                <div class="mx-auto tooltip" data-tip="Waiting response from marketplace">
                                    <div class="w-8 h-8 mx-auto"><Clock /></div>
                                </div>
                            {:else if bid.backendResponse.status === 'accepted'}
                                <div class="text-xl mx-auto tooltip" data-tip="Bid confirmed">✅</div>
                            {:else if bid.backendResponse.status === 'rejected'}
                                <div class="text-xl mx-auto tooltip" data-tip="Bid rejected: {bid.backendResponse.message}">❌</div>
                            {:else if bid.backendResponse.status === 'pending'}
                                <div class="w-8 h-8 mx-auto text-xl tooltip" data-tip="{ bid.backendResponse.badge_stall_id ? "Bid pending: Skin in the Game required" : "Bid pending: " + bid.backendResponse.message }"><Clock /></div>
                                {#if bid.pubkey === $NostrPublicKey}
                                    <div>
                                        <button class="btn btn-sm btn-success" on:click|preventDefault={() => openSitgBadgeInfo(bid.backendResponse.badge_stall_id, bid.backendResponse.badge_product_id, true)}>Skin in the Game required</button>
                                    </div>
                                {/if}
                            {:else if bid.backendResponse.status === 'winner'}
                                <div class="text-xl mx-auto tooltip" data-tip="{bid.backendResponse.winnerPubkey === $NostrPublicKey ? 'Congratulations!' : 'This is the winning bid'}"><div class="w-8 h-8 mx-auto"><WinnerBadge /></div></div>
                            {:else}
                                Unknown response from the marketplace
                            {/if}
                        </td>
                        <th class="{bid.backendResponse && bid.backendResponse.status === 'winner' ? winnerColor + ' font-bold' : 'font-normal'}">
                            <a href="/p/{nip19.npubEncode(bid.pubkey)}"
                               target="_blank"
                               class="underline">
                                <div class="flex items-center space-x-3 p-3"
                                     on:mouseenter={(e) => {hoverTimer=window.setTimeout(function(){showUserProfilePopup(e, bid.pubkey)},250)}}
                                     on:mouseleave={hideUserProfilePopup}
                                >
                                    <div class="avatar mask mask-squircle w-12 h-12 cursor-pointer">
                                        <img src={userProfileInfoMap.get(bid.pubkey)?.picture ?? profilePicturePlaceHolder}
                                             on:error={(event) => onImgError(event.srcElement, profilePicturePlaceHolder)}>
                                             alt="Avatar of the identity that made the bid"
                                        />
                                    </div>
                                    <div class="flex">
                                        {userProfileInfoMap.get(bid.pubkey)?.name?.substring(0,30) ?? bid.pubkey.substring(0,12) + '...'}
                                        {#if userProfileInfoMap.get(bid.pubkey)?.nip05VerifiedAddress}
                                            <span class="mt-1 ml-2">
                                                <Nip05Checkmark address="{userProfileInfoMap.get(bid.pubkey).nip05VerifiedAddress}" />
                                            </span>
                                        {/if}
                                    </div>
                                </div>
                            </a>
                        </th>
                    </tr>
                {/if}
            {/each}
            </tbody>
        </table>
    </div>
{/if}


<dialog id="user_information_modal" class="modal">
    <div class="modal-box">
        {#if mobile}
            <UserInfoPopup bind:userPubkey={modalPubkey} />
        {/if}
    </div>
</dialog>

<div id="user-information-popup" transition:fade|global class:absolute={modalPubkey} class:opacity-0={!modalPubkey} class:opacity-100={modalPubkey} class="w-96 m-4 transition-opacity ease-in-out delay-75 duration-200 card card-compact z-[200] bg-base-200 border-2 border-neutral-content/50 shadow shadow-neutral-content/50 ">
    <div class="card-body">
        {#if !mobile}
            <UserInfoPopup bind:userPubkey={modalPubkey} />
        {/if}
    </div>
</div>

