<script lang="ts">
    const weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

    export let date: Date | undefined;
</script>

<span>
    {#if date}
        {weekdays[date.getDay()]} {date.toLocaleString('default', { month: 'long' })} {date.getDate()}, {date.getHours()}:{date.getMinutes().toString().padStart(2, "0")}
    {/if}
</span>
