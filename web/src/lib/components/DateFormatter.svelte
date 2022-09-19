<script context="module" lang="ts">
    export enum DateStyle {
        Short,
        Long
    }
</script>

<script lang="ts">
    const weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    export let date: Date | undefined;
    export let style: DateStyle = DateStyle.Long;
</script>

<span>
    {#if date}
        {#if style === DateStyle.Long}
            <span class="inline-block w-0 lg:w-auto invisible lg:visible">{weekdays[date.getDay()]}</span> {date.toLocaleString('default', { month: 'long' })} {date.getDate()}, {date.getHours()}:{date.getMinutes().toString().padStart(2, "0")}
        {:else if style === DateStyle.Short}
            {date.toLocaleString('default', { month: 'short' })} {date.getDate()}
            {#if date.getFullYear() !== new Date().getFullYear()}
                {date.getFullYear()}
            {/if}
            {date.getHours()}:{date.getMinutes().toString().padStart(2, "0")}
        {/if}
    {/if}
</span>
