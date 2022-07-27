<script lang="ts">
    export let date: Date | undefined;
</script>

<span>
    {#if date}
        {date.toLocaleString('default', { month: 'short' })} {date.getDate()}, {date.getHours()}:{date.getMinutes().toString().padStart(2, "0")}
    {/if}
</span>
