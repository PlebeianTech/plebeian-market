<script lang="ts">
    const weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    export let date: Date | undefined;
</script>

<span>
    {#if date}
        <span class="inline-block w-0 lg:w-auto invisible lg:visible">{weekdays[date.getDay()]}</span> {date.toLocaleString('default', { month: 'long' })} {date.getDate()}, {date.getHours()}:{date.getMinutes().toString().padStart(2, "0")}
    {/if}
</span>
