<svelte:head>
    <title>Enter the Market</title>
</svelte:head>

<script lang="ts">
    import { goto } from "$app/navigation";
    import Login from "../lib/components/Login.svelte";
    import type { User } from "../lib/types/user";

    function onLogin(user: User | null) {
        goto("/");
    }
</script>

<Login onLogin={onLogin} />
