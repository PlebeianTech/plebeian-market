<script>
    import Slider from '@bulatdashiev/svelte-slider';

    import { fetchAPI, token, ContributionPercent } from "../common.js";

    let value = $ContributionPercent !== null ? [$ContributionPercent, $ContributionPercent] : [10, 10];

    export let onSave = () => {};

    function saveProfile() {
        fetchAPI("/users/me", 'POST', $token,
            JSON.stringify({contribution_percent: value[0]}),
            (response) => {
                if (response.status === 200) {
                    response.json().then(data => {
                        ContributionPercent.set(data.user.contribution_percent);
                        onSave();
                    });
                }
            });
    }
</script>

<div class="flex justify-center items-center h-screen">

<div class="w-1/2">
<div class="pt-5">
    <Slider min="0" max="100" step="5" bind:value />
</div>

<div class="text-2xl text-zinc-300 text-center">
{ value[0] }
</div>
<div class="text-4xl text-center">
{#if value[0] === 0}
    {@html "&#x1F4A9;"}
{:else if value[0] < 10}
    {@html "&#x1F625;"}
{:else if value[0] < 20}
    {@html "&#x1F615;"}
{:else if value[0] < 30}
    {@html "&#x1F610;"}
{:else if value[0] < 60}
    {@html "&#x1F609;"}
{:else if value[0] < 100}
    {@html "&#x1F60D;"}
{:else if value[0] === 100}
    {@html "&#x1F631;"}
{/if}
</div>

<div class="flex justify-center items-center">
    <div class="glowbutton glowbutton-save mt-2" on:click|preventDefault={saveProfile}></div>
</div>
</div>

</div>