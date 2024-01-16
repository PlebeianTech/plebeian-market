<script context="module" lang="ts">
    export enum CountdownStyle {
        Large,
        Compact
    }
</script>

<script lang="ts">
    import { onDestroy, onMount } from 'svelte';

    export let style: CountdownStyle = CountdownStyle.Large;

    export let ended: boolean;
    export let totalSeconds: number | null = null;

    let secondsRemanining: number | null = totalSeconds;

    let timeWhenTotalSecondsWasReceived = Date.now();

    let days, hours, minutes, seconds;

    $: lastMinute = (days === 0) && (hours === 0) && (minutes === 0);

    function refresh() {
        if (totalSeconds === null) {
            return;
        }

        secondsRemanining = totalSeconds - ((Date.now() - timeWhenTotalSecondsWasReceived) / 1000);

        if (secondsRemanining > 0) {
            days = Math.floor(secondsRemanining / 86400);
            secondsRemanining -= days * 86400;

            hours = Math.floor(secondsRemanining / 3600) % 24;
            secondsRemanining -= hours * 3600;

            minutes = Math.floor(secondsRemanining / 60) % 60;
            secondsRemanining -= minutes * 60;

            seconds = Math.floor(secondsRemanining % 60);
        } else {
            days = hours = minutes = seconds = 0;
            ended = true;
        }
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
        {#if style !== CountdownStyle.Compact || days !== 0 || hours !== 0}
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