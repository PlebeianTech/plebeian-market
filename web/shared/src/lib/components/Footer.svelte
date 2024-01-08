<script lang="ts">
    import Nostr from "$sharedLib/components/icons/Nostr.svelte";
    import Twitter from "$sharedLib/components/icons/Twitter.svelte";
    import Telegram from "$sharedLib/components/icons/Telegram.svelte";
    import Github from "$sharedLib/components/icons/Github.svelte";
    import Substack from "$sharedLib/components/icons/Substack.svelte";

    export let isFrontOffice = true;
</script>

<footer class="text-neutral-content bg-neutral border-t border-white/20 p-4 pb-0" data-sveltekit-preload-data="hover">
    <div class="lg:w-2/3 mx-auto w-full lg:flex items-center justify-between py-4 pb-0">
        <div>
            <span class="lg:text-4xl text-3xl font-bold">Plug into the Bitcoin Economy</span>
            <div class="lg:flex lg:space-x-4 my-6 gap-4 mt-2">
                <p>&#10003; Built for Nostr</p>
                <p>&#10003; Bitcoin only</p>
                <p>&#10003; Lightning tech</p>
                <p>&#10003; Value4Value</p>
                <p>&#10003; Peer2Peer</p>
            </div>
        </div>
        <div class="grid space-y-1 mt-6 md:mt-0 justify-center">
            <div>
                <a class="btn btn-ghost align-middle size-16" target="_blank" rel="noreferrer" href="https://snort.social/p/npub1market6g3zl4mxwx5ugw56hfg0f7dy7jnnw8t380788mvdyrnwuqgep7hd">
                    <Nostr />
                </a>
                <a class="btn btn-ghost align-middle" target="_blank" rel="noreferrer" href="https://plebeianmarket.substack.com/">
                    <Substack />
                </a>
                <a class="btn btn-ghost align-middle" target="_blank" rel="noreferrer" href="https://t.me/PlebeianMarket">
                    <Telegram />
                </a>
                <a class="btn btn-ghost align-middle" target="_blank" rel="noreferrer" href="https://twitter.com/PlebeianMarket">
                    <Twitter />
                </a>
                <a class="btn btn-ghost align-middle" target="_blank" rel="noreferrer" href="https://github.com/PlebeianTech/plebeian-market">
                    <Github />
                </a>
            </div>
            <div class="mt-4 text-2xl">
                <a href="/faq" rel="{isFrontOffice ? '' : 'external'}" class="btn btn-ghost normal-case text-lg">FAQ</a> -
                <a href="/contact" rel="{isFrontOffice ? '' : 'external'}" class="btn btn-ghost normal-case text-lg">Contact</a> -
                <a href="/about" rel="{isFrontOffice ? '' : 'external'}" class="btn btn-ghost normal-case text-lg">About</a>
            </div>
        </div>
    </div>
</footer>
