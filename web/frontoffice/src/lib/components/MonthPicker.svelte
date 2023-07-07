<script lang="ts">
    export let value: number | null = null;

    let monthNames: string[] = [];
    for (let i = 0; i < 12; i++) {
        monthNames.push(new Date(2020 /* the year here is irrelevant... */, i, 1).toLocaleString('default', { month: 'long' }));
    }
</script>

<select bind:value={value} class="select select-bordered w-full max-w-xs">
    <option></option>
    {#each monthNames as monthName, i}
        <option value={i + 1}>{monthName}</option>
    {/each}
</select>
