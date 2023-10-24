<script lang="ts">
    import VerificationMark from "$sharedLib/components/icons/VerificationMark.svelte";

    export let address = '';
    export let verificationMarkSize = "4";
</script>

<div class="dropdown dropdown-left dropdown-hover dropdown-end z-[100]">
    <label tabindex="0" class="hover:cursor-pointer hover:scale-110 duration-300">
        <div class="w-{verificationMarkSize} h-{verificationMarkSize} text-blue-700 opacity-70">
            <VerificationMark />
        </div>
    </label>
    <ul tabindex="0" class="dropdown-content translate-x-20">
        <div class="badge badge-accent whitespace-nowrap pt-0">{address}</div>
    </ul>
</div>
