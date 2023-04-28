<script lang="ts">
    import BadgeSVG from "$lib/components/BadgeSVG.svelte";
    export let campaign_name: string | null;
</script>

<h3 class="font-bold text-lg">Skin in the game</h3>
<p class="py-4">
    In order to bid over $500 we ask plebs for a
    {#if campaign_name !== null}
        one-time donation to the campaign,
    {:else}
        one-time fee,
    {/if}
    the equivalent of $50... this has two benefits:
</p>
<ul class="list-disc mt-2 ml-2">
    <li>It shows that you are a committed participant</li>
    <li>It deters spam</li>
</ul>
{#if campaign_name !== null}
    <p class="py-4">
        The money will go directly to the <span class="badge badge-primary mb-4">{campaign_name} campaign</span>
    </p>
{/if}
<p class="py-4">
    You will get this badge in your profile to prove to other users you have Skin in the Game:
    <BadgeSVG badge={{badge: 0, icon: 'SKIN_IN_THE_GAME'}} />
</p>