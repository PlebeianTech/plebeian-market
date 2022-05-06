<script>
    import { goto } from "$app/navigation";
    import Login from "../Login.svelte";
</script>

<Login onLogin={() => goto("/auctions")} />
