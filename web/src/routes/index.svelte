<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script>
    	import Typewriter from 'svelte-typewriter'
</script>
<div class="flex justify-center">
<div class="mt-4 md:columns-3 w-3/5">
    <div class="flex"><div class="text-9xl">1.</div><div class="h-full text-4xl">Tweet Photos</div></div>
    <div class="flex"><div class="text-9xl">2.</div><div class="h-full text-4xl">Click Start</div></div>
    <div class="flex"><div class="text-9xl">3.</div><div class="h-full text-4xl">Collect Sats</div></div>
</div>
</div>
<div class="flex justify-center">
<div class="mt-12 columns-3 w-3/4">
    <span>
        <p class="flex-row text-3xl text-right">Sell anything...</p>
    </span>
    <span class="flex bg-black/30">
<Typewriter interval={[50, 60, 95, 80]} cursor='255,255,255,30' loop>
<p class="text-3xl">1 hour of your time</p>
<p class="text-3xl">bitcoin art</p>
<p class="text-3xl">your furniture</p>
<p class="text-3xl">an ASIC miner</p>
<p class="text-3xl">Baklava</p>
<p class="text-3xl">your next book</p>
</Typewriter>
    </span>
    <span>
        <p class="text-3xl text-left">...and get paid in sats.</p>
    </span>
</div>
</div>

<div class="pt-10 flex justify-center items-center">
    <a class="btn" href="/login">Enter the market!</a>
</div>
