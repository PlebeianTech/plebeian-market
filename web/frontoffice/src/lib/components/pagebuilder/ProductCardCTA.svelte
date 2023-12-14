<script lang="ts">
    import productImageFallback from "$lib/images/product_image_fallback.svg";
    import Plus from "$sharedLib/components/icons/Plus.svelte";
</script>

<div class="relative grid h-[40rem] max-h-48 md:max-h-[32rem] w-full max-w-[28rem] flex-col items-end justify-center overflow-hidden rounded-md md:rounded-xl bg-white bg-clip-border text-center text-gray-700">
    <a class="cursor-pointer hover:underline" href="/admin">
        <div class="absolute inset-0 m-0 h-full w-full overflow-hidden rounded-none bg-transparent bg-cover bg-clip-border bg-center text-gray-700 shadow-none">
            <span class="w-7/12 mt-4 md:mt-20 text-green-500 cursor-pointer tooltip">
                <Plus />
            </span>
            <div class="absolute p-2 pt-1 md:p-4 bottom-0 left-0 right-0 h-30 bg-black bg-opacity-30 backdrop-blur text-white rounded-b-lg">
                <h1 class="text-md md:text-2xl leading-4">Add your own product!</h1>
                <p class="mt-1 md:mt-2 text-xs md:text-lg">Do you want to sell or auction your own products? Click here!</p>
            </div>
        </div>
    </a>
</div>
