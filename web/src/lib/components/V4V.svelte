<script>
    export let contributionPercent;
</script>

<div class="flex items-center justify-center mt-8">
    <div>
        <div class="form-control w-full max-w-lg">
            <label class="label" for="contribution-percent">
                <span class="label-text">Value4Value contribution</span>
            </label>
            <div>
                <input type="range" min="0" max="5" bind:value={contributionPercent} class="range" step="0.5" />
                <div class="w-full flex justify-between text-xs px-2">
                <span>|</span>
                <span>|</span>
                <span>|</span>
                <span>|</span>
                <span>|</span>
                <span>|</span>
                </div>
            </div>
            <label class="label" for="contribution-percent">
                <span class="label-text w-2/4">Generosity enables us to continue creating free and open source solutions!</span>
                <span class="label-text text-right w-2/4">100% goes to powering the Bitcoin movement!</span>
            </label>
        </div>

        <div class="text-2xl text-center">
            { contributionPercent }%
        </div>

        <div class="text-4xl text-center">
            {#if contributionPercent === 0}
                {@html "&#x1F4A9;"}
            {:else if contributionPercent < 2}
                {@html "&#x1F625;"}
            {:else if contributionPercent < 3}
                {@html "&#x1F615;"}
            {:else if contributionPercent < 4}
                {@html "&#x1F610;"}
            {:else if contributionPercent <= 4.5}
                {@html "&#x1F642;"}
            {:else if contributionPercent <= 5}
                {@html "&#x1F60D;"}
            {/if}
        </div>
    </div>
</div>