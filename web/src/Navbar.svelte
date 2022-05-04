<script>
    import { token } from "./stores.js";

    export let onSelect = (key) => {};
</script>

<div class="navbar bg-base-100">
    <div class="flex-1">
        <a href={null} on:click|preventDefault={() => onSelect('app')} class="btn btn-ghost normal-case text-xl">Home</a>
        <a href={null} on:click|preventDefault={() => onSelect('about')} class="btn btn-ghost normal-case text-xl">About</a>
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
                    <li><a href={null} on:click|preventDefault={() => onSelect('profile')}>Profile</a></li>
                    <li><a href={null} on:click|preventDefault={() => onSelect('logout')}>Logout</a></li>
                </ul>
            </div>
        {/if}
    </div>
  </div>