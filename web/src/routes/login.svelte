<script lang="ts">
    import MetaTag from "$lib/components/MetaTag.svelte";
    import { goto } from "$app/navigation";
    import Login from "../lib/components/Login.svelte";
    import type { User } from "../lib/types/user";

    export let title = "Enter the Market";

    function onLogin(user: User | null) {
        if (user && user.twitterUsername === null) {
            localStorage.setItem('initial-login-seller', "1");
        }
        goto("/auctions");
    }
</script>

<svelte:head>
    <MetaTag {title} />
</svelte:head>

<Login onLogin={onLogin} />
