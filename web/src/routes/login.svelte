<svelte:head>
    <title>Enter the Market</title>
</svelte:head>

<script lang="ts">
    import { goto } from "$app/navigation";
    import Login from "../lib/components/Login.svelte";
    import type { User } from "../lib/types/user";

    function onLogin(user: User | null) {
        if (user && user.twitterUsername === null) {
            localStorage.setItem('initial-login-seller', "1");
        }
        goto("/stall");
    }
</script>

<Login onLogin={onLogin} />
