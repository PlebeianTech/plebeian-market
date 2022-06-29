<script>
    export let amount;
</script>

{#if amount >= 1000000}
    {#if amount % 1000000 === 0}
        <span>{amount / 1000000}M</span>
    {:else}
        <span>{amount.toLocaleString('en')}</span>
    {/if}
{:else if amount >= 1000}
    {#if amount % 1000 === 0}
        <span>{amount / 1000}k</span>
    {:else}
        <span>{amount.toLocaleString('en')}</span>
    {/if}
{:else}
    <span>{amount}</span>
{/if}