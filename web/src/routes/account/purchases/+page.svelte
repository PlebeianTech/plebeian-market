<script lang="ts">
    import { fromJson as saleFromJson } from "$lib/types/sale";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import PurchaseRow from "$lib/components/PurchaseRow.svelte";
</script>

<h1 class="lg:text-8xl font-bold text-4xl text-center my-20">My purchases</h1>

<div class="lg:w-2/3 mx-auto">

  <ListView
      loader={{endpoint: "users/me/purchases", responseField: 'purchases', fromJson: saleFromJson}}
      columns={["Date", "Seller", "Item", "Sats / Fiat", "Sent sats ($ shipping)", "State"]}
      card={PurchaseRow}
      editor={null}
      extraClasses="w-11/12 mt-4"
      style={ListViewStyle.Table} />
</div>
