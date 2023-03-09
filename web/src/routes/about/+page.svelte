<script lang="ts">
</script>

<svelte:head>
    <title>About</title>
</svelte:head>

<!-- HERO -->
<div class="bg-fixed bg-center bg-cover bg-no-repeat bg-[url('$lib/images/golden-gai-tokyo.jpg')]">
    <div class="bg-gradient-to-b from-black/70 to-black/70">
        <div class="lg:w-2/3 mx-auto py-20 p-4">
            <div class="lg:w-1/2 mx-auto lg:text-3xl text-white my-20 text-center">
                <h1 class="lg:text-8xl text-8xl font-bold my-4">About</h1>
                <p>Plebeian Market is a distributed, self-sovereign P2P marketplace.</p>
            </div>
        </div>
    </div>
</div>

<div class="lg:w-1/2 mx-auto p-4 mt-20">
    <blockquote class="lg:text-7xl text-4xl font-bold mt-2 md:mt-10 p-4 italic border-l-4 quote">
        <p>"You will own your market stall and you will be happy."</p>
    </blockquote>
</div>

<div class="flex justify-center items-centermy-20 py-20">
    <div class="mt-10 lg:w-2/3 p-2 grid lg:grid-cols-2 gap-4 leading-10">
        <!-- COL -->
        <div class="mt-2 md:mt-10">
            <ul>
                <li>Value4Value business model...</li>
                <li>100% of the donations to this site go into funding open source Bitcoin projects.</li>
                <li>Sellers decide how much of their sale they want to donate.</li>
                <li>The buyer pays it in settlement of the auction they won or the product they bought.</li>
            </ul>
        </div>

        <!-- COL -->
        <div class="mt-2 md:mt-10">
            <ul>
                <li>This site is FOSS and is initially released under the GNU General Public License (GPL).</li>
                <li>Once we have completed the MVPs for the other components of the ecosystem we will transition to a more permissive license, most likely MIT.</li>
            </ul>
        </div>
    </div>
</div>

<h2 class="text-center my-16 lg:text-8xl font-bold text-4xl">Team</h2>
<div class="lg:w-2/3 mx-auto grid lg:grid-cols-3 gap-4 my-20 p-4">
    <a class="bg-gray-300/20 p-4 rounded hover:scale-95 duration-300" target="_blank" rel="noreferrer" href="https://snort.social/p/npub1a3um269aaf3u5cy37kuykrrrnsg2pyv7za06pxjduv25lq5sdujs2qmdj6">
        <h2 class="text-3xl font-bold my-4">Chiefmonkey</h2>
        <h3 class="uppercase my-2 font-bold text-sm">Founder</h3>
    </a>

    <a class="bg-gray-300/20 p-4 rounded hover:scale-95 duration-300" target="_blank" rel="noreferrer" href="https://snort.social/p/npub1lxpdhu4q5jjgfjvvtjachqapajhktzwtyefwryupzk94v3h7y0tqtx73vg">
        <h2 class="text-3xl font-bold my-4">ibz</h2>
        <h3 class="uppercase my-2 font-bold text-sm">Senior Developer</h3>
    </a>

    <a class="bg-gray-300/20 p-4 rounded hover:scale-95 duration-300" target="_blank" rel="noreferrer" href="https://twitter.com/BitkoYinowsky">
        <h2 class="text-3xl font-bold my-4">Bitko Yinowsky</h2>
        <h3 class="uppercase my-2 font-bold text-sm">Artist</h3>
    </a>

    <a class="bg-gray-300/20 p-4 rounded hover:scale-95 duration-300" target="_blank" rel="noreferrer" href="https://snort.social/p/npub1qw6sxmwrmwpxqsc8cxty62ujvst6j8pmz8hhtwnv54gpn6dh5c4qms4882">
        <h2 class="text-3xl font-bold my-4">Luis Miguel</h2>
        <h3 class="uppercase my-2 font-bold text-sm">Senior Developer</h3>
    </a>

    <a class="bg-gray-300/20 p-4 rounded hover:scale-95 duration-300" target="_blank" rel="noreferrer" href="https://snort.social/p/npub18ekka6n399pskjzjusvduscem5c99dewg2swe3u68vdce92cmxgszeht3g">
        <h2 class="text-3xl font-bold my-4">Bekka</h2>
        <h3 class="uppercase my-2 font-bold text-sm">Communications</h3>
    </a>

    <a class="group bg-gray-300/20 p-4 rounded hover:scale-150 duration-300" href={null}>
        <h2 class="text-3xl font-bold my-4">You?</h2>
        <p class="visible group-hover:visible lg:invisible lg:group-hover:visible text-xl font-bold my-4"><a class="link" href="/contact">Contact us!</a></p>
        <h3 class="uppercase my-2 font-bold text-sm">Bitcoiner, remnant and shadowy super coder</h3>
    </a>
</div>
