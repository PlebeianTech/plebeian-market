<script lang="ts">
    import VerificationMark from "$sharedLib/components/icons/VerificationMark.svelte";

    export let address: string;
</script>

<div class="dropdown dropdown-bottom dropdown-hover dropdown-end">
    <label tabindex="0" class="hover:cursor-pointer hover:scale-110 duration-300">
        <div class="w-4 h-4 text-blue-700 opacity-70">
            <VerificationMark />
        </div>
    </label>
    <ul tabindex="0" class="dropdown-content translate-x-20">
        <li>
            <div class="badge badge-accent whitespace-nowrap">{address}</div>
        </li>
    </ul>
</div>
