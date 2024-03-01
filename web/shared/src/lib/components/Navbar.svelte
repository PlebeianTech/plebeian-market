<script lang="ts">
    import { onMount } from 'svelte';
    import {page} from "$app/stores";
    import { afterNavigate } from "$app/navigation";
    import {
        NostrPublicKey,
        privateMessages,
        ShoppingCart,
        BTC2USD,
        isSuperAdmin,
        fileConfiguration, NostrGlobalConfig
    } from "$sharedLib/stores";
    import { getValue } from 'btc2fiat';
    import {isProduction, getEnvironmentInfo, logout, requestLoginModal} from "$sharedLib/utils";
    import Modal from "$sharedLib/components/Modal.svelte";
    import CompactShoppingCart from "$lib/components/stores/ShoppingCart.svelte";
    import PrivateMessages from "$sharedLib/components/nostr/PrivateMessages.svelte";
    import ProfilePicture from "$sharedLib/components/nostr/ProfilePicture.svelte";
    import ShoppingCartIcon from "$sharedLib/components/icons/ShoppingCart.svelte";
    import Settings from "$sharedLib/components/icons/Settings.svelte";
    import Store from "$sharedLib/components/icons/Store.svelte";
    import User from "$sharedLib/components/icons/User.svelte";
    import World from "$sharedLib/components/icons/World.svelte";
    import Moon from "$sharedLib/components/icons/Moon.svelte";
    import Sun from "$sharedLib/components/icons/Sun.svelte";
    import Home from "$sharedLib/components/icons/Home.svelte";
    import Cash from "$sharedLib/components/icons/Cash.svelte";
    import Exit from "$sharedLib/components/icons/Exit.svelte";
    import Book from "$sharedLib/components/icons/Book.svelte";
    import Chat from "$sharedLib/components/icons/Chat.svelte";
    import Key from "$sharedLib/components/icons/Key.svelte";
    import Support from "$sharedLib/components/icons/Support.svelte";
    import Identities from "$sharedLib/components/icons/Identities.svelte";
    import Info from "$sharedLib/components/icons/Info.svelte";
    import FiatChooser from "$sharedLib/components/FiatChooser.svelte";
    import {getConfigurationKey, subscribeConfiguration} from "$sharedLib/services/nostr";
    import {getPages, pagesAndTitles} from "$sharedLib/pagebuilder";
    // import Tools from "$sharedLib/components/icons/Tools.svelte";

    export let isFrontOffice = true;

    let modal: Modal | null;

    let prefersDark = false;

    let showMobileMenu = false;

    let allPagesNavbarList = [];

    function toggleMobileMenu() {
        showMobileMenu = !showMobileMenu;

        document.body.style.overflow = showMobileMenu ? 'hidden' : '';
    }

    function hideMobileMenu() {
        showMobileMenu = false;

        document.body.style.overflow = '';
    }

    function toggleTheme() {
        let html = <HTMLHtmlElement>document.querySelector("html");

        if (!prefersDark) {
            html.dataset.theme = "dark";
            localStorage.theme = "dark";
        } else {
            html.dataset.theme = "light";
            localStorage.theme = "light";
        }
    }

    async function fetchFiatRate() {
        BTC2USD.set(await getValue());
    }

    let logoURL = '/images/logo.png';
    let siteTitle = 'Plebeian Market';
    $: {
        if ($NostrGlobalConfig?.content?.logo) {
            logoURL = $NostrGlobalConfig.content.logo;
        } else {
            logoURL = '/images/logo.png';
        }

        if ($NostrGlobalConfig?.content && $NostrGlobalConfig?.content.hasOwnProperty('title')) {
            siteTitle = $NostrGlobalConfig.content.title;
        } else {
            siteTitle = '';
        }
    }

    let virtualPages;

    onMount(async () => {
        if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            prefersDark = true;
        } else {
            prefersDark = false;
        }

        virtualPages = getPages();

        let retries = 5;
        while ((!$fileConfiguration || Object.keys($fileConfiguration).length === 0) && retries-- > 0) {
            await new Promise(resolve => setTimeout(resolve, 30));
        }

        if ($fileConfiguration?.admin_pubkeys?.length > 0) {
            let allPagesListReceivedAt = 0;

            subscribeConfiguration($fileConfiguration.admin_pubkeys, [getConfigurationKey('navbar_config')],
                (navbarConfigFromNostr, rcAt) => {
                    if (rcAt > allPagesListReceivedAt) {
                        allPagesListReceivedAt = rcAt;
                        allPagesNavbarList = navbarConfigFromNostr;
                    }
                });
        }

        if (!isFrontOffice) {
            fetchFiatRate();
        }
    });

    afterNavigate(() => {
        hideMobileMenu();
    });
</script>

<nav class="fixed top-0 w-full backdrop-blur-3xl border-b border-gray-400/70 z-50" data-sveltekit-preload-data="hover">
    <div class="3xl:w-11/12 p-2 mx-auto lg:flex lg:flex-row flex-col md:justify-between md:items-center">
        <div class="flex items-center justify-between">
            <a href="/" rel="{isFrontOffice ? '' : 'external'}" class="flex items-center mr-2 indicator">
                <div class="flex items-center space-x-2">
                    <img src={logoURL} class="mr-3 h-14 rounded" alt="Plebeian Technology" />
                    {#if !isProduction()}
                        <span class="indicator-item badge badge-error">{getEnvironmentInfo().substring(0,3)}</span>
                    {/if}
                    {#if siteTitle}
                        <h1 class="w-52 2xl:w-64 3xl:w-72 text-base lg:text-lg 2xl:text-xl font-bold hover:text-blue-400 duration-300">
                            {siteTitle}
                        </h1>
                    {/if}
                </div>
            </a>

            <!-- LINKS -->
            <div class="hidden lg:flex items-right w-full">
                {#if allPagesNavbarList.length === 0}
                    <p class="ml-24 mr-8">
                        <a href="/stalls" rel="{isFrontOffice ? '' : 'external'}" class="btn btn-ghost normal-case {$page.url.pathname === '/stalls' ? 'underline' : ''}">Stall Browser</a>
                    </p>
                    <!--
                    <p class="mr-8">
                        <a href="/skills" class="btn btn-ghost normal-case">Skills Market</a>
                    </p>
                    -->
                    <p class="mr-8">
                        <a href="/marketsquare" rel="{isFrontOffice ? '' : 'external'}" class="btn btn-ghost normal-case {$page.url.pathname === '/marketsquare' ? 'underline' : ''}">Market Square</a>
                    </p>
                    <p class="mr-8">
                        <a href="/planet" rel="{isFrontOffice ? '' : 'external'}" class="btn btn-ghost normal-case {$page.url.pathname === '/planet' ? 'underline' : ''}">Plebeian Planet</a>
                    </p>
                    {#if $isSuperAdmin}
                        <p class="mr-8">
                            <a href="/universe" rel="{isFrontOffice ? '' : 'external'}" class="btn btn-ghost normal-case {$page.url.pathname === '/universe' ? 'underline' : ''}">Nostr Universe</a>
                        </p>
                    {/if}
                {:else}
                    <p class="ml-24"></p>
                    {#each allPagesNavbarList as page}
                        {#if page.enabled}
                            <p class="mr-8">
                                {#if page.p_id.startsWith('virt-') && virtualPages}
                                    <!-- Virtual page -->
                                    <a href="/{virtualPages[page.p_id.substring(5)]?.slug ?? ''}" rel="{isFrontOffice ? '' : 'external'}" class="btn btn-ghost normal-case ">{virtualPages[page.p_id.substring(5)]?.title ?? ''}</a>
                                {:else}
                                    <!-- Real page -->
                                    <a href="/{page.p_id}" rel="{isFrontOffice ? '' : 'external'}" class="btn btn-ghost normal-case ">{pagesAndTitles[page.p_id]?.title ?? '------'}</a>
                                {/if}
                            </p>
                        {/if}
                    {/each}
                {/if}
            </div>

            <!-- Mobile menu button -->
            <div on:click={toggleMobileMenu} on:keydown={toggleMobileMenu} class="lg:hidden flex justify-end p-2 -mr-3">
                <button type="button" class="text-black-800 dark:text-gray-200 focus:outline-none">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                    </svg>
                </button>

                {#if $ShoppingCart.summary.totalQuantity || $privateMessages.unreadConversations}
                    <span class="indicator-item badge badge-sm badge-error -ml-3">
                        {Number($ShoppingCart.summary.totalQuantity ?? 0) + Number($privateMessages.unreadConversations ?? 0)}
                    </span>
                {/if}
            </div>
        </div>

        {#if isFrontOffice}
            <div class="right-0 mr-3 3xl:mr-5 hidden lg:block">
                <FiatChooser />
            </div>
        {/if}

        <div class:flex={showMobileMenu} class:hidden={!showMobileMenu} class="lg:flex lg:flex-row flex-col justify-center space-y-0">
            <div class="lg:flex items-center justify-start 3xl:space-x-2">
                <div class="float-right">
                    {#if isFrontOffice}
                        <div class="right-0 lg:hidden">
                            <FiatChooser />
                        </div>
                    {/if}

                    <label tabindex="0" class="swap swap-rotate mr-2 3xl:mr-3" on:click={toggleTheme} on:keypress={toggleTheme}>
                        <input type="checkbox" bind:checked={prefersDark} />
                        <div class="swap-off size-8 3xl:size-9"><Sun /></div>
                        <div class="swap-on size-8 3xl:size-9"><Moon /></div>
                    </label>

                    <div class="btn btn-ghost btn-circle mr-1 3xl:mr-3">
                        <PrivateMessages />
                    </div>

                    {#if isFrontOffice}
                        <div class="dropdown dropdown-end mr-1 3xl:mr-3">
                            <label tabindex="0" class="btn btn-ghost btn-circle">
                                <div class="size-7 3xl:size-8 focus:outline-none indicator" >
                                    <ShoppingCartIcon />
                                    {#if $ShoppingCart.summary.totalQuantity}
                                        <span class="badge badge-sm badge-info indicator-item">{$ShoppingCart.summary.totalQuantity}</span>
                                    {/if}
                                </div>
                            </label>
                            <div tabindex="0" class="!fixed lg:float w-[97%] lg:w-fit mt-0 mr-1 bg-base-300 card card-compact card-bordered border-black dark:border-white dropdown-content shadow-xl z-50">
                                <div class="card-body !px-2">
                                    <CompactShoppingCart compact={true} />
                                </div>
                            </div>
                        </div>
                    {/if}
                </div>

                <div class="lg:dropdown lg:dropdown-end h-screen lg:h-fit clear-both" on:click={hideMobileMenu} on:keydown={hideMobileMenu}>
                    {#if $NostrPublicKey }
                        <ProfilePicture />
                    {:else}
                        <!-- Desktop menu button -->
                        <label tabindex="0" class="btn btn-circle swap swap-rotate hidden md:grid">
                            <!-- this hidden checkbox controls the state -->
                            <input type="checkbox" />
                            <!-- hamburger icon -->
                            <svg class="swap-off fill-current size-8" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M64,384H448V341.33H64Zm0-106.67H448V234.67H64ZM64,128v42.67H448V128Z"/></svg>
                            <!-- close icon -->
                            <svg class="swap-on fill-current size-8" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><polygon points="400 145.49 366.51 112 256 222.51 145.49 112 112 145.49 222.51 256 112 366.51 145.49 400 256 289.49 366.51 400 400 366.51 289.49 256 400 145.49"/></svg>
                        </label>
                    {/if}

                    <ul role="menuitem" tabindex="0" class="float-right right-2 w-60 z-40 p-2 shadow menu menu-compact dropdown-content bg-base-300 text-accent-contend rounded-box md:border border-neutral-300">
                        {#if !$NostrPublicKey}
                            <li class="text-primary">
                                <a href={null} class="modal-button cursor-pointer text-base" on:click={() => {requestLoginModal(); hideMobileMenu()}} on:keypress={() => {requestLoginModal(); hideMobileMenu()}}>
                                    <span class="size-6 mr-1 stroke-primary"><Key /></span> <b>Login</b>
                                </a>
                            </li>
                        {/if}
                        <li class="block md:hidden md:h-0">
                            <a href="/planet" rel="{isFrontOffice ? '' : 'external'}" class="modal-button cursor-pointer text-base">
                                <div class="size-6 mr-1"><World /></div> Plebeian Planet
                            </a>
                        </li>
                        {#if $isSuperAdmin}
                            <li class="block md:hidden md:h-0">
                                <a href="/universe" rel="{isFrontOffice ? '' : 'external'}" class="modal-button cursor-pointer text-base">
                                    <div class="size-6 mr-1"><World /></div> Nostr Universe
                                </a>
                            </li>
                        {/if}
                        {#if $NostrPublicKey}
                            <li class="menu-title pb-0">
                                <span class="text-lg">Account</span>
                            </li>
                            <li>
                                <a class="text-base" rel="{isFrontOffice ? '' : 'external'}" href="/p/{$NostrPublicKey}">
                                    <div class="size-6 mr-1"><User /></div> Me
                                </a>
                            </li>
                        {/if}
                        {#if !isFrontOffice || (isFrontOffice && $fileConfiguration.backend_present)}
                            <li>
                                <a class="text-base" rel="{isFrontOffice ? 'external' : ''}" href="/admin">
                                    <div class="size-6 mr-1"><Store /></div> Stall Manager
                                </a>
                            </li>
                        {/if}
                        {#if $NostrPublicKey}
                            <li>
                                <a class="text-base" href="/orders">
                                    <span class="size-6 mr-1"><Cash /></span> My purchases
                                </a>
                            </li>
                            <li>
                                <a class="text-base" rel="{isFrontOffice ? 'external' : ''}" href="/admin/account/orders/">
                                    <span class="size-6 mr-1"><Cash /></span> My sales
                                </a>
                            </li>
                            {#if $isSuperAdmin}
                                <li>
                                    <a class="text-base" href="/cms">
                                        <span class="size-6 mr-1"><Settings /></span> CMS
                                    </a>
                                </li>
                            {/if}
                            <li>
                                <a class="text-base" href="/verification">
                                    <span class="size-6 mr-1"><Identities /></span> Get Verified
                                </a>
                            </li>
                            <li>
                                <a class="text-base" href="/nostr">
                                    <span class="size-6 mr-1"><Info /></span> Nostr Info
                                </a>
                            </li>
                            <li>
                                <a class="text-base" rel="{isFrontOffice ? 'external' : ''}" href="/admin/account/settings">
                                    <span class="size-6 mr-1"><Settings /></span> Settings
                                </a>
                            </li>
                            <li>
                                <a href={null} on:click={() => {logout(); hideMobileMenu()}} class="modal-button cursor-pointer text-base">
                                    <span class="size-6 mr-1"><Exit /></span> Logout
                                </a>
                            </li>
                        {/if}
                        <li class="block md:hidden md:h-0 menu-title pb-0">
                            <span class="text-lg">Community</span>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/" rel="{isFrontOffice ? '' : 'external'}" class="modal-button cursor-pointer text-base">
                                <span class="size-6 mr-1"><Home /></span> Home
                            </a>
                        </li>
                        <li class="block md:hidden md:h-0">
                            <a href="/stalls" rel="{isFrontOffice ? '' : 'external'}" class="modal-button cursor-pointer text-base">
                                <div class="size-6 mr-1"><Store /></div> Stall Browser
                            </a>
                        </li>
                        <!--
                        <li class="block md:hidden md:h-0">
                            <a href="/skills" rel="{isFrontOffice ? '' : 'external'}" class="modal-button cursor-pointer text-base">
                                <div class="size-6 mr-1"><Tools /></div> Skills Market
                            </a>
                        </li>
                        -->
                        <li class="block md:hidden md:h-0">
                            <a href="/marketsquare" rel="{isFrontOffice ? '' : 'external'}" class="modal-button cursor-pointer text-base">
                                <div class="size-6 mr-1"><Chat /></div> Market Square
                            </a>
                        </li>
                        {#if $NostrPublicKey}
                            <li class="menu-title text-base pb-0">
                                <span class="text-lg">Other information</span>
                            </li>
                        {/if}

                        <li>
                            <a href="/faq" rel="{isFrontOffice ? '' : 'external'}" class="modal-button cursor-pointer text-base">
                                <span class="size-6 mr-1"><Book /></span> FAQ
                            </a>
                        </li>
                        <li>
                            <a href="/donations" rel="{isFrontOffice ? '' : 'external'}" class="text-base">
                                <div class="size-6 mr-1"><Support /></div> Support Us
                            </a>
                        </li>
                        <li>
                            <a href="/contact" rel="{isFrontOffice ? '' : 'external'}" class="text-base">
                                <div class="size-6 mr-1"><Chat /></div> Contact
                            </a>
                        </li>
                        <li>
                            <a href="/about" rel="{isFrontOffice ? '' : 'external'}" class="modal-button cursor-pointer text-base">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6 mr-1">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z" />
                                </svg>
                                About
                            </a>
                        </li>
                        {#if !isProduction()}
                            <li class="block md:hidden md:h-0 text-primary">
                                <span class="text-base">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="size-6 mr-1">
                                        <path fill-rule="evenodd" d="M11.097 1.515a.75.75 0 01.589.882L10.666 7.5h4.47l1.079-5.397a.75.75 0 111.47.294L16.665 7.5h3.585a.75.75 0 010 1.5h-3.885l-1.2 6h3.585a.75.75 0 010 1.5h-3.885l-1.08 5.397a.75.75 0 11-1.47-.294l1.02-5.103h-4.47l-1.08 5.397a.75.75 0 01-1.47-.294l1.02-5.103H3.75a.75.75 0 110-1.5h3.885l1.2-6H5.25a.75.75 0 010-1.5h3.885l1.08-5.397a.75.75 0 01.882-.588zM10.365 9l-1.2 6h4.47l1.2-6h-4.47z" clip-rule="evenodd" />
                                    </svg>
                                    <b>{getEnvironmentInfo()}</b>
                                </span>
                            </li>
                        {/if}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</nav>

<Modal bind:this={modal} content={null} />
