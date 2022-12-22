<script lang="ts">
    export let campaign_name: string | null;
</script>

<h3 class="font-bold text-lg">Skin in the game</h3>
<p class="py-4">
    In order to bid over $500 we ask plebs for a 1-time fee, the equivalent of $50... this has two benefits:
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