<script lang="ts">
    import type { IEntity } from "$lib/types/base";
    import type { Relay } from "$lib/types/relay";

    // svelte-ignore unused-export-let
    export let isEditable: boolean = false;
    export let entity: IEntity;
    $: relay = <Relay>(<unknown>entity);
</script>

<tr>
    <td>
        {relay.url}
    </td>
</tr>
