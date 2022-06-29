<script lang="ts">
    import Typewriter from 'svelte-typewriter';
</script>

<style global>
    :global(:root) {
        --cursor-color: #00ff00;
        --cursor-width: 0.2ch;
    }
</style>

<span>
    <p class="mt-2 md:mt-0 text-xl text-center lg:text-3xl md:text-right mr-0 md:mr-1">Sell anything...</p>
</span>
<span class="flex justify-center">
    <Typewriter interval={[50, 60, 95, 80]} cursor='255,255,255,30' loop>
        <span class="text-neon-pink justify-center text-xl lg:text-3xl">
            <p>1 hour of your time</p>
            <p>Bitcoin art</p>
            <p>your chair</p>
            <p>an ASIC miner</p>
            <p>baklava</p>
            <p>your next book</p>
        </span>
    </Typewriter>
</span>
<span class="text-xl text-center md:translate-x-1 md:text-left md:text-xl lg:text-3xl">
    <p>and get paid in sats.</p>
</span>
