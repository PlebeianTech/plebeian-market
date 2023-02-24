<script lang="ts">
    import { fromJson as saleFromJson } from "$lib/types/sale";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import SaleRow from "$lib/components/SaleRow.svelte";
</script>

<h3 class="lg:text-8xl font-bold text-center text-4xl my-20">My sales</h3>

<div class="lg:w-2/3 mx-auto">
  <ListView
      loader={{endpoint: "users/me/sales", responseField: 'sales', fromJson: saleFromJson}}
      columns={["Date", "Buyer", "Item", "Sats / Fiat", "Received sats ($ shipping)", "State"]}
      card={SaleRow}
      editor={null}
      extraClasses="w-11/12 mt-4"
      style={ListViewStyle.Table} />
</div>
