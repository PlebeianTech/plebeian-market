  
  
  <!-- HERO SECTION STATIC CONTENT -->
  <div id="bgHero" class="bg-fixed">
    <!-- FILTER -->
    <div class="bg-gradient-to-b from-black/60 to-pink-500/70">
      <div class="lg:w-2/3 mx-auto grid lg:grid-cols-2 gap-4">
        <!-- COL -->
        <div class="mt-20 p-4">
          <!-- FULL WIDTH BANNER -->
          <!-- <img src={BannerImg} alt=""> -->
          <h2 class="lg:text-7xl text-4xl font-bold text-white">{title}</h2>
          <!-- <h1 class="lg:text-2xl font-bold mt-4">Get started</h1> -->
          <a href="#anchorId" on:click|preventDefault={scrollIntoView} class="btn btn-primary uppercase font-bold my-8">Auction 1-hour of your time</a>
          <div class="mb-8">
            <!-- <p class="text-3xl">OR</p> -->
            <div class="space-x-1">
              <a href="#anchorId" on:click|preventDefault={scrollIntoView} class="btn btn-outline text-white uppercase font-bold my-4">Auction Item</a>
              <a href="#anchorIdFixedPrice" on:click|preventDefault={scrollIntoView} class="btn btn-outline text-white uppercase font-bold my-4">Fixed Price</a>
            </div>
          </div>
    
          <!-- AVATARS -->
          <div class="flex space-x-4">
            <div class="avatar flex">
              <div class="w-16 rounded">
                <img src="https://placeimg.com/192/192/people" alt="image" />
              </div>
            </div>
            <div class="avatar">
              <div class="w-16 rounded">
                <img src="https://placeimg.com/192/192/people" alt="Tailwind-CSS-Avatar-component" />
              </div>
            </div>
            <div class="avatar">
              <div class="w-16 rounded">
                <img src="https://placeimg.com/192/192/people" alt="Tailwind-CSS-Avatar-component" />
              </div>
            </div>
          </div>
          
          <div class="my-4">
            <!-- <lottie-player
              src="https://assets1.lottiefiles.com/packages/lf20_6mveojb1.json"
              background="transparent"
              speed="1"
              loop
              autoplay
              class=""
              style="width: 100px; height: 100px"
            ></lottie-player> -->
          </div>
        </div>
    
        <div class="grid place-items-center">
          <img src={Faketoshi} alt="hero-image">
        </div>
        </div>
   
    </div>
    </div>