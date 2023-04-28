<script>
    import { user } from "$lib/stores";
    import { Campaign, fromJson } from "$lib/types/campaign";
    import CampaignCard from "$lib/components/CampaignCard.svelte";
    import CampaignEditor from "$lib/components/CampaignEditor.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
</script>

{#if $user && $user.isModerator}
    <div class="grid place-items-center py-20 lg:w-2/3 mx-auto p-2">

        <h3 class="lg:text-8xl text-5xl font-bold">My campaigns</h3>

        <ListView
                loader={{endpoint: 'users/me/campaigns', responseField: 'campaigns', fromJson}}
                postEndpoint="users/me/campaigns"
                card={CampaignCard}
                editor={CampaignEditor}
                style={ListViewStyle.List}>
            <div slot="new-entity" class="flex justify-center" let:setCurrent={setCurrent}>
                <button class="mx-auto my-10 btn btn-primary" on:click|preventDefault={() => setCurrent(new Campaign())}>Create a new Campaign</button>
            </div>
        </ListView>
    </div>
{:else}
    <div class="alert alert-info shadow-lg mt-8">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>Please contact us if you want to launch a campaign!</span>
        </div>
    </div>
{/if}