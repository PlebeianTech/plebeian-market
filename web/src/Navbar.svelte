<script>
    import { goto } from '$app/navigation';
    import { token } from "./stores.js";
</script>

<div class="navbar bg-base-300">
    <div class="flex-1">
        <a href={null} on:click|preventDefault={() => goto("/")} class="btn btn-ghost normal-case text-xl">Home</a>
        <a href={null} on:click|preventDefault={() => goto("/about")} class="btn btn-ghost normal-case text-xl">About</a>
    </div>
    <div class="flex-none gap-2">
        {#if $token}
            <div class="dropdown dropdown-end">
                <label for={null} tabindex="0" class="btn btn-ghost btn-circle avatar">
                    <div class="w-10 rounded-full">
                        <img src="https://api.lorem.space/image/face?hash=33791" alt="Avatar" />
                    </div>
                </label>
                <ul tabindex="0" class="mt-3 p-2 shadow menu menu-compact dropdown-content bg-base-100 rounded-box w-52">
                    <li><a href={null} on:click|preventDefault={() => goto("/auctions")}>My auctions</a></li>
                    <li><a href={null} on:click|preventDefault={() => goto("/profile")}>Profile</a></li>
                    <li><a href={null} on:click|preventDefault={() => { token.set(null); localStorage.removeItem('token'); goto("/"); }}>Logout</a></li>
                </ul>
            </div>
        {/if}
    </div>
  </div>