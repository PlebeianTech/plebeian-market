<script lang="ts">
    import { fromJson as saleFromJson } from "$lib/types/sale";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import SaleRow from "$lib/components/SaleRow.svelte";
</script>

<h3 class="text-xl">My sales</h3>

<ListView
    loader={{endpoint: `users/me/sales`, responseField: 'sales', fromJson: saleFromJson}}
    showNewButton={false}
    columns={["Date", "Title", "Quantity", "Price (USD)", "Sats", "Received sats ($ shipping)", "Buyer", "State", "Transaction"]}
    card={SaleRow}
    editor={null}
    extraClasses="w-11/12 mt-4"
    style={ListViewStyle.Table} />
