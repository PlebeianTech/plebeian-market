<script lang="ts">
    export let hasDetail = false;
    let detailVisible = false;
</script>

<div class="alert alert-error shadow-lg">
    <div>
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        <div>
            <slot />
            {#if hasDetail && detailVisible}
                <slot name="detail" />
            {/if}
        </div>
    </div>
    <div>
        {#if hasDetail && !detailVisible}
            <div class="text-center">
                <a href={null} class="link text-center" on:click={() => detailVisible = true}>Read more</a>
            </div>
        {/if}
    </div>
</div>
