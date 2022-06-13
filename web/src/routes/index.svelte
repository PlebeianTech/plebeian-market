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
<div class="flex justify-center">
<div class="mt-12 columns-1 md:columns-3 md:w-11/12">
    <span>
        <p class="flex-row text-s md:text-xl lg:text-3xl lg:text-right">Sell anything...</p>
    </span>
    <span class="flex bg-black/30">
<Typewriter interval={[50, 60, 95, 80]} cursor='255,255,255,30' loop>
        <span class="text-s md:text-xl lg:text-3xl">
            <p>1 hour of your time</p>
            <p>bitcoin art</p>
            <p>your furniture</p>
            <p>an ASIC miner</p>
            <p>Baklava</p>
            <p>your next book</p>
        </span>
</Typewriter>
    </span>
    <span>
        <p class="text-s md:text-xl lg:text-3xl text-left">...and get paid in sats.</p>
    </span>
</div>
</div>

<div class="pt-10 flex justify-center items-center">
    <a class="btn" href="/login">Enter the market!</a>
</div>
