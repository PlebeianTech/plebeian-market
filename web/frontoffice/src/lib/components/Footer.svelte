<script lang="ts">
    import Nostr from "$sharedLibComponents/icons/Nostr.svelte";
    import Twitter from "$sharedLibComponents/icons/Twitter.svelte";
    import Telegram from "$sharedLibComponents/icons/Telegram.svelte";
    import Github from "$sharedLibComponents/icons/Github.svelte";
    import Substack from "$sharedLibComponents/icons/Substack.svelte";
</script>

<footer class="text-neutral-content bg-neutral border-t border-white/20 p-4 pb-0">
    <div class="lg:w-2/3 mx-auto w-full lg:flex items-center justify-between py-4 pb-0">
        <div>
            <h1 class="lg:text-4xl text-3xl font-bold">Plug into the Bitcoin Economy</h1>
            <div class="lg:flex lg:space-x-4 my-6">
                <p>&#10003; Built for Nostr</p>
                <p>&#10003; Bitcoin only</p>
                <p>&#10003; Lightning tech</p>
                <p>&#10003; Value4Value</p>
                <p>&#10003; Peer2Peer</p>
            </div>
        </div>
        <div class="grid items-center space-y-2">
            <div>
                <a target="_blank" rel="noreferrer" href="https://plebeianmarket.substack.com/">
                    <button class="btn border-2 border-white flex items-center">
                        <Substack />
                        <p class="mx-2">
                            Substack &#8702;
                        </p>
                    </button>
                </a>
            </div>
            <div>
                <a class="btn btn-ghost align-middle" target="_blank" rel="noreferrer" href="https://snort.social/p/npub1market6g3zl4mxwx5ugw56hfg0f7dy7jnnw8t380788mvdyrnwuqgep7hd">
                    <Nostr />
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
        </div>
    </div>
</footer>
