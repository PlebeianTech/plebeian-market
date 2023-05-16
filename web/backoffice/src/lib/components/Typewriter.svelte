<script lang="ts">
    import Typewriter from 'svelte-typewriter';
</script>

<style global>
    :global(:root) {
        --cursor-color: #00ff00;
        --cursor-width: 0.2ch;
    }
</style>

<div class="text-neutral-content">
  <span>
      <p class="text-6xl lg:text-8xl">Sell anything...</p>
  </span>
  <div class="flex text-8xl my-4 lg:justify-start justify-center">
      <Typewriter interval={60} cursor={true} mode="loop">
          <span class="text-neon-pink justify-center text-xl lg:text-3xl">
              <p>1 hour of your time</p>
              <p>Bitcoin art</p>
              <p>your chair</p>
              <p>an ASIC miner</p>
              <p>baklava</p>
              <p>your next book</p>
          </span>
      </Typewriter>
  </div>
  <span class="text-xl text-center md:translate-x-1 md:text-left md:text-xl lg:text-3xl">
      <p>and get paid in sats.</p>
  </span>
</div>
