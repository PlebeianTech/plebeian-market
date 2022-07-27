<svelte:head>
    <title>Stores</title>
</svelte:head>

<script lang="ts">

</script>

<div class="pt-16 px-64">
    <!-- top profile section -->
    <div class="flex space-x-12">
        <div class="rounded-full border border-accent-400 avatar h-32 mt-4 ml-12">
            <img src="/images/test-profile.jpg" class="w-32 rounded-full" alt="Avatar"/>
        </div>
        <div>
            <div class="flex items-center justify-center">
                <div class="flex space-x-4">
                    <!-- Link to social -->
                    <span class="font-thin text-3xl">
                        @bit_hodl_coin
                    </span>
                    <!-- if logged in and looking at your store -->
                    <span class="btn btn-ghost">
                        Configure Store
                    </span>
                </div>
            </div>
            <div class="flex justify-between pt-3">
                <span class="text-sm font-semibold">10 Active Listings</span>
                <span class="text-sm font-semibold">5 Active Auctions</span>
                <span class="text-sm font-semibold">19 Past Auctions</span>
            </div>
            <div class="pt-6 grid">
                <span class="text-2xl semibold">Ye Old Gun Store</span>
                <span class="font-thin">we sell really nice guns for bear hunting</span>
            </div>
        </div>
    </div>
    <!-- store listing section -->
    <hr class="border-solid border-accent divide-y-0 opacity-50 my-5">
    <div class="tabs flex space-x-4 items-center justify-center">
        <span class="tab tab-bordered text-sm font-semibold">ALL</span>
        <span class="tab text-sm font-semibold">FOR SALE</span>
        <span class="tab text-sm font-semibold">FOR AUCTION</span>
    </div>
    <div class="pt-6 pb-6">
        <div class="grid grid-cols-3 gap-2">
            <div>
                <img src="/images/test-profile.jpg" alt="listing"/>
            </div>
            <div>
                <img src="/images/test-profile.jpg" alt="listing"/>
            </div>
            <div>
                <img src="/images/test-profile.jpg" alt="listing"/>
            </div>
            <div>
                <img src="/images/test-profile.jpg" alt="listing"/>
            </div>
            <div>
                <img src="/images/test-profile.jpg" alt="listing"/>
            </div>
            <div>
                <img src="/images/test-profile.jpg" alt="listing"/>
            </div>
            <div>
                <img src="/images/test-profile.jpg" alt="listing"/>
            </div>
            <div>
                <img src="/images/test-profile.jpg" alt="listing"/>
            </div>
        </div>
    </div>
</div>