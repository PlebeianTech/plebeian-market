<script lang="ts">
    import MetaTag from "$lib/components/MetaTag.svelte";

    export let title = "About";
</script>

<svelte:head>
    <MetaTag title={title} />
</svelte:head>

<div class="flex justify-center items-center md:mb-20">
    <div class="mt-10 ml-4 w-3/4 md:text-3xl">
        <p class="mt-2 md:mt-10">This is an MVP and an incidental idea on the way to a fully sovereign version... it's the first piece of a much bigger vision of decentralised sovereign commerce.</p>
        <p class="mt-2 md:mt-10">100% Value4Value business model... 100% donations to this site go into open source bitcoin projects.</p>
        <p class="mt-2 md:mt-10">Sellers decide how much of their sale they want to donate. The buyer pays it in settlement of the auction they won or the product they bought.</p>
        <p class="mt-2 md:mt-10">This site is FOSS and will initially be released under the GNU General Public License (GPL). Once we have completed the MVPs for the other components of the ecosystem we will transition to a more permissive license, most likely MIT.</p>
        <p class="mt-2 md:mt-10">We are <a class="link" target="_blank" href="https://twitter.com/HodlrDotRocks">Chiefmonkey</a>, <a class="link" target="_blank" href="https://twitter.com/ibz">ibz</a>, <a class="link" target="_blank" href="https://twitter.com/RompHenry">Henry Romp</a> and <a class="link" target="_blank" href="https://twitter.com/BitkoYinowsky">Bitko Yinowsky</a>.</p>
    </div>
</div>
