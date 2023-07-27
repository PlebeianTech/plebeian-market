<script lang="ts">
    import { user } from "$lib/stores";
    import { fromJson as relayFromJson } from "$lib/types/relay";
    import InfoBox from "$lib/components/notifications/InfoBox.svelte";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import RelayRow from "$lib/components/RelayRow.svelte";

    export const onSave: () => void = () => {};
</script>

<div class="text-2xl breadcrumbs">
    <ul>
        <li>Settings</li>
        <li>Nostr</li>
    </ul>
</div>

{#if $user}
    <InfoBox>
        These are the relays we are currently using to publish your products. This list is currently not editable, but please contact us if you want to include additional relays.
    </InfoBox>
    <ListView
        loader={{endpoint: "relays", responseField: 'relays', fromJson: relayFromJson}}
        columns={["URL"]}
        card={RelayRow}
        editor={null}
        style={ListViewStyle.Table} />
{/if}
