<script lang="ts">
    import MetaTags from "$lib/components/MetaTags.svelte";
    import { goto } from "$app/navigation";
    import Login from "../lib/components/Login.svelte";
    import type { User } from "../lib/types/user";
    import { browser } from "$app/env";

    let title = "Enter the Market | Plebeian Market";

    function onLogin(user: User | null) {
        if (user && user.twitterUsername === null && browser) {
            localStorage.setItem('initial-login-seller', "1");
        }
        goto("/auctions");
    }
</script>

<svelte:head>
    <MetaTags {title} />
</svelte:head>

<Login onLogin={onLogin} />
