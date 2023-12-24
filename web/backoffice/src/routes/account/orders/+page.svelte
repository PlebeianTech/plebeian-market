<script lang="ts">
    import { fromJson as orderFromJson } from "$lib/types/order";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import OrderRow from "$lib/components/OrderRow.svelte";
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
</script>

<Titleh1>My received orders</Titleh1>

<div class="w-full mx-auto">
    <ListView
        loader={{endpoint: "users/me/orders", responseField: 'orders', fromJson: orderFromJson}}
        columns={["Order ID", "Date", "Order Total", "Amount Collected", "Buyer", "Status", "Actions"]}
        headerAlignment="text-center"
        card={OrderRow}
        editor={null}
        style={ListViewStyle.Table} />
</div>
