<script lang="ts">
    import Product from "$lib/components/stores/Product.svelte";
    import { browser } from "$app/environment";

    export let viewProductIdOnModal: string | null = null;
    export let scrollPosition: number | null = null;

    $: if (browser && window.view_product_modal) {
        if (viewProductIdOnModal === null) {
            window.view_product_modal.close();

            if (scrollPosition !== null) {
                restoreScroll();
            }
        } else {
            history.pushState({
                viewProductIdOnModal: viewProductIdOnModal
            }, "Product page", "/product/" + viewProductIdOnModal);
            window.view_product_modal.showModal();
        }
    }

    function close() {
        viewProductIdOnModal = null;
        history.back();
    }

    async function restoreScroll() {
        await new Promise(resolve => setTimeout(resolve, 250));
        document.documentElement.scrollTop = scrollPosition;
    }
</script>

<dialog id="view_product_modal" class="modal">
    <form method="dialog" class="modal-box w-[97%] aaaaw-11/12 aaaaw-full max-w-full">
        <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2" on:click|preventDefault={close}>✕</button>
        {#key `${viewProductIdOnModal}`}
            {#if viewProductIdOnModal}
                {#key viewProductIdOnModal}
                    <Product product_id={viewProductIdOnModal} in_popup={true} />
                {/key}
            {/if}
        {/key}
        <div class="modal-action">
            <button class="btn" on:click|preventDefault={close}>Close</button>
        </div>
    </form>
</dialog>