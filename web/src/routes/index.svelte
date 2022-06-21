<svelte:head>
    <title>Plebeian Market</title>
</svelte:head>

<script>
        import Typewriter from 'svelte-typewriter'
</script>
<div class="flex justify-center">
<div class="mt-4 md:columns-3 w-3/5">
    <div class="flex items-center mt-2">
        <div class="text-7xl ml-9 md:ml-0 md:text-9xl">1</div>
        <div class="flex flex-col">
            <div><img class="max-h-24 ml-4 md:ml-0 md:max-h-48 " src="/images/bitko_01.png" alt="Tweet!"></div>
            <div class="h-full ml-2 text-xl">Tweet Photos</div>
        </div>
    </div>
    <div class="flex items-center mt-2">
        <div class="text-7xl ml-9 md:ml-0 md:text-9xl">2</div>
        <div class="flex flex-col">
            <div><img class="max-h-24 ml-4 md:ml-0 md:max-h-48" src="/images/bitko_02.png" alt="Start!"></div>
            <div class="h-full ml-2 text-xl">Click Start</div>
        </div>
    </div>
    <div class="flex items-center mt-2">
        <div class="text-7xl ml-9 md:ml-0 md:text-9xl">3</div>
        <div class="flex flex-col">
            <div><img class="max-h-24 ml-4 md:ml-0 md:max-h-48" src="/images/bitko_03.png" alt="Stack!"></div>
            <div class="h-full ml-2 text-xl">Stack Sats</div>
        </div>
    </div>
</div>
</div>
<div class="md:ml-20 md:flex md:justify-center md:justify-items-start mt-12 px-8 columns-1 gap-0 md:columns-3 md:w-11/12">
    <span>
        <p class="mr-1 text-s text-center md:text-xl lg:text-3xl md:text-right">Sell anything...</p>
    </span>
    <span class="flex justify-center">
<Typewriter interval={[50, 60, 95, 80]} cursor='255,255,255,30' loop>
        <span class="text-neon-pink justify-center text-s md:text-xl lg:text-3xl">
            <p>1 hour of your time</p>
            <p>Bitcoin art</p>
            <p>your chair</p>
            <p>an ASIC miner</p>
            <p>baklava</p>
            <p>your next book</p>
        </span>
</Typewriter>
    </span>
    <span class="-translate-x-2 text-s text-center md:text-left md:text-xl lg:text-3xl">
        <p>and get paid in sats.</p>
    </span>
</div>
<div class="pt-10 mb-3 text-2xl flex justify-center ">Let's get the market started...</div>
<div class="flex justify-center items-center">
    <div class="glowbutton glowbutton-go mb-5" on:click={() => { window.location.href = `${window.location.protocol}//${window.location.host}/login`; }}></div>
</div>
