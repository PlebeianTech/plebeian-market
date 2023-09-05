<script lang="ts">
    import badgeImageFallback from "$sharedLib/images/badge_placeholder.svg";

    export let onImgError = () => {};
    export let badgeInfo;
</script>

<dialog id="badge_modal" class="modal">
    {#if badgeInfo}
        <div class="modal-box w-11/12 max-w-3xl">
            <form method="dialog">
                <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
            </form>
            <div class="flex w-full">
                <div class="grid flex-grow place-items-center">
                    <figure class="avatar mask mask-squircle h-32 w-32 md:h-72 md:w-72">
                        <img id="badgeModalImg" src={badgeInfo.image ?? badgeImageFallback} on:load={(event) => {console.log('onLoad', event.srcElement); event.srcElement.style.visibility="visible"}} on:error={(event) => onImgError(event.srcElement)} alt="" />
                    </figure>
                </div>
                <div class="grid flex-grow place-items-center ml-4 md:ml-12">
                    <p class="font-bold text-xl md:text-2xl mb-3">{badgeInfo.name}</p>
                    <p class="text-lg md:text-xl align-top">{badgeInfo.description}</p>
                </div>
            </div>
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    {/if}
</dialog>