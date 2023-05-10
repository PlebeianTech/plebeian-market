<script lang="ts">
    export let value: number | null = null;

    export let yearsBack = 50;
    export let includeCurrentYear = true;

    let years: number[] = [];
    if (includeCurrentYear) {
        years.push(parseInt(new Date().toLocaleString('default', { year: 'numeric' })));
    }
    let today = new Date();
    for (let i = 1; i < yearsBack; i++) {
        years.push(parseInt(new Date(today.getFullYear() - i, today.getMonth(), 1).toLocaleString('default', {year: 'numeric'})));
    }
</script>

<select bind:value={value} class="select select-bordered w-full max-w-xs">
    <option></option>
    {#each years as year}
        <option value={year}>{year}</option>
    {/each}
</select>