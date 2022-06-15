<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script>
        import Typewriter from 'svelte-typewriter'
</script>
<div class="flex justify-center">
<div class="mt-4 md:columns-3 w-3/5">
    <div class="flex"><div class="text-7xl lg:text-9xl">1.</div><div class="h-full text-2xl lg:text-4xl">Tweet Photos</div></div>
    <div class="flex"><div class="text-7xl lg:text-9xl">2.</div><div class="h-full text-2xl lg:text-4xl">Click Start</div></div>
    <div class="flex"><div class="text-7xl lg:text-9xl">3.</div><div class="h-full text-2xl lg:text-4xl">Collect Sats</div></div>
</div>
</div>
<div class="md:ml-20 md:flex md:justify-center md:justify-items-start mt-12 px-8 columns-1 gap-0 md:columns-3 md:w-11/12">
    <span>
        <p class="text-s text-center md:text-xl lg:text-3xl md:text-right">Sell anything...</p>
    </span>
    <span class="flex justify-center">
<Typewriter interval={[50, 60, 95, 80]} cursor='255,255,255,30' loop>
        <span class="text-pink-500 justify-center text-s md:text-xl lg:text-3xl">
            <p>1 hour of your time</p>
            <p>bitcoin art</p>
            <p>your furniture</p>
            <p>an ASIC miner</p>
            <p>Baklava</p>
            <p>your next book</p>
        </span>
</Typewriter>
    </span>
    <span class="-translate-x-2 text-s text-center md:text-left md:text-xl lg:text-3xl">
        <p>and get paid in sats.</p>
    </span>
</div>

<div class="pt-10 flex justify-center items-center">
    <div class="glowbutton glowbutton-sell-and-stack mb-5" on:click={() => { window.location.href = `${window.location.protocol}//${window.location.host}/login`; }}></div>
</div>
