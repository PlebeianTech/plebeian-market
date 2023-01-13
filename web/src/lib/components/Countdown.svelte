<script context="module" lang="ts">
    export enum CountdownStyle {
        Large,
        Compact
    }
</script>

<script lang="ts">
    import { onDestroy, onMount } from 'svelte';

    export let totalSeconds: number | null = null;

    export let style: CountdownStyle = CountdownStyle.Large;

    let days, hours, minutes, seconds;

    $: lastMinute = (days === 0) && (hours === 0) && (minutes === 0);

    export function isLastMinute() {
        return lastMinute;
    }

    function refresh() {
        if (totalSeconds === null) {
            return;
        }

        totalSeconds--;

        if (totalSeconds < 0) {
            totalSeconds = 0;
        }

        var delta = totalSeconds;
        days = Math.floor(delta / 86400);
        delta -= days * 86400;
        hours = Math.floor(delta / 3600) % 24;
        delta -= hours * 3600;
        minutes = Math.floor(delta / 60) % 60;
        delta -= minutes * 60;
        seconds = delta % 60;
    }

    let interval: ReturnType<typeof setInterval> | undefined;

    onMount(async () => {
        refresh();
        interval = setInterval(refresh, 1000);
    });

    onDestroy(() => {
        if (interval) {
            clearInterval(interval);
            interval = undefined;
        }
    });
</script>

<div class:blink={lastMinute} class="flex justify-center items-center" class:gap-5={style !== CountdownStyle.Compact} class:gap-1={style === CountdownStyle.Compact}>
    {#if !lastMinute}
        {#if style !== CountdownStyle.Compact || days !== 0}
            <div>
                <span class="countdown font-mono" class:text-3xl={style === CountdownStyle.Large}>
                    <span style="--value:{days};"></span>
                </span>
                {#if style !== CountdownStyle.Compact}
                    days
                {/if}
            </div>
            {#if style === CountdownStyle.Compact}
                d
            {/if}
        {/if}
        <div>
            <span class="countdown font-mono" class:text-3xl={style === CountdownStyle.Large}>
                <span style="--value:{hours};"></span>
            </span>
            {#if style !== CountdownStyle.Compact}
                hours
            {/if}
        </div>
        {#if style === CountdownStyle.Compact}
            :
        {/if}
        <div>
            <span class="countdown font-mono" class:text-3xl={style === CountdownStyle.Large}>
                <span style="--value:{minutes};"></span>
            </span>
            {#if style !== CountdownStyle.Compact}
                min
            {/if}
        </div>
        {#if style === CountdownStyle.Compact}
            :
        {/if}
    {/if}
    <div>
        <span class="countdown font-mono" class:text-5xl={lastMinute && style === CountdownStyle.Large}>
            <span style="--value:{seconds};"></span>
        </span>
        {#if style !== CountdownStyle.Compact}
            sec
        {/if}
    </div>
</div>