<script lang="ts">
  import { scale } from "svelte/transition";

  function scrollIntoView({ target }) {
      const el = document.querySelector(target.getAttribute('href'))
      if (!el) return;
      el.scrollIntoView({
        behavior: 'smooth'
      })
    }
</script>

<svelte:head>
    <title>About</title>
</svelte:head>


<!-- HERO -->
<div id="aboutHero" class="bg-fixed">
  <div class="bg-gradient-to-b from-black/70 to-black/70">
    <div class="lg:w-2/3 mx-auto py-20 p-4">
      <div class="lg:w-1/2 mx-auto lg:text-3xl text-white my-20 text-center">
        <h1 class="lg:text-8xl text-8xl font-bold my-4">About</h1>
        <p>Plebeian Market is a distributed self sovereign P2P market place.</p>
          <!-- <a href="#team" on:click|preventDefault={scrollIntoView}>
            <button class="btn btn-primary my-8">Go to Team</button>
          </a> -->
      </div>
    </div>

  </div>
</div>

<div class="lg:w-1/2 mx-auto p-4 mt-20">
  <blockquote class="lg:text-7xl text-4xl font-bold mt-2 md:mt-10 p-4 italic border-l-4 bg-neutral-100 text-neutral-600 border-neutral-500 quote">
    <p>"You will own your market stall and you will be happy."</p>
  </blockquote>
</div>

<div class="flex justify-center items-centermy-20 py-20">
    <div class="mt-10 lg:w-2/3 p-2 grid lg:grid-cols-2 gap-4 leading-10">

      <!-- COL -->
      <div>
        <p class="mt-2 md:mt-10">100% Value-4-Value business model... 100% donations to this site go into open source bitcoin projects.
          Sellers decide how much of their sale they want to donate. The buyer pays it in settlement of the auction they won or the product they bought.
        </p>
      </div>

      <!-- COL -->
      <div>
        <p class="mt-2 md:mt-10">This site is FOSS and will initially be released under the GNU General Public License (GPL). Once we have completed the MVPs for the other components of the ecosystem we will transition to a more permissive license, most likely MIT.</p>
      </div>
        
    </div>
</div>

<!-- TEAM -->
<div id="team" class="mt-8" />
<h2 class="text-center my-16 lg:text-8xl font-bold text-4xl">Team</h2>
<div class="lg:w-2/3 mx-auto grid lg:grid-cols-3 gap-4 my-20 p-4">
  <!-- COL -->
  <a class="bg-gray-300/20 p-4 rounded cardHover duration-300" target="_blank" rel="noreferrer" href="https://twitter.com/HodlrDotRocks">

    <h2 class="text-3xl font-bold my-4">Chiefmonkey</h2>
    <h3 class="uppercase my-2 font-bold text-sm">Chief</h3>

  </a>

  <!-- COL -->
  <a class="bg-gray-300/20 p-4 rounded cardHover duration-300" target="_blank" rel="noreferrer" href="https://twitter.com/ibz">

    <h2 class="text-3xl font-bold my-4">ibz</h2>
    <h3 class="uppercase my-2 font-bold text-sm">Senior Developer</h3>

  </a>

  <!-- COL -->
  <a class="bg-gray-300/20 p-4 rounded cardHover duration-300" target="_blank" rel="noreferrer" href="https://twitter.com/BitkoYinowsky">

    <h2 class="text-3xl font-bold my-4">Bitko Yinowsky</h2>
    <h3 class="uppercase my-2 font-bold text-sm">Artist</h3>

  </a>

  <!-- COL -->
  <a class="bg-gray-300/20 p-4 rounded cardHover duration-300" target="_blank" rel="noreferrer" href="https://twitter.com/btc_remnant">

    <h2 class="text-3xl font-bold my-4">Luis Miguel</h2>
    <h3 class="uppercase my-2 font-bold text-sm">Senior Developer</h3>

  </a>

  <!-- COL -->
  <a class="bg-gray-300/20 p-4 rounded cardHover duration-300" target="_blank" rel="noreferrer" href="https://twitter.com/GhostOfBekka">

    <h2 class="text-3xl font-bold my-4">Bekka</h2>
    <h3 class="uppercase my-2 font-bold text-sm">Communications</h3>

  </a>

  <!-- COL -->
  <a class="bg-gray-300/20 p-4 rounded cardHover duration-300" href="https://twitter.com/j__khan" target="_blank" rel="noreferrer">

    <h2 class="text-3xl font-bold my-4">Jay Khan</h2>
    <h3 class="uppercase my-2 font-bold text-sm">Front-end Developer</h3>
  </a>
</div>

<style>
  #aboutHero {
    background-image: url('$lib/images/golden-gai-tokyo.jpg');
    background-position: center;
    background-size: cover;
    background-repeat: no-repeat;
  }

  .cardHover:hover {
    scale: 95%
  }
</style>