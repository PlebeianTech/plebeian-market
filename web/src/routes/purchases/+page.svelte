<script lang="ts">
    import { fromJson as saleFromJson } from "$lib/types/sale";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import PurchaseRow from "$lib/components/PurchaseRow.svelte";
</script>

<h3 class="text-4xl my-4 ml-2">My purchases</h3>

<ListView
    loader={{endpoint: "users/me/purchases", responseField: 'purchases', fromJson: saleFromJson}}
    columns={["Date", "Seller", "Item", "Sats / Fiat", "Sent sats ($ shipping)", "State"]}
    card={PurchaseRow}
    editor={null}
    extraClasses="w-11/12 mt-4"
    style={ListViewStyle.Table} />
