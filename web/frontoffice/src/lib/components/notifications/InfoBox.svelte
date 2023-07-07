<script lang="ts">
    import AlertInfo from "$sharedLib/components/icons/AlertInfo.svelte";
</script>
<div class="alert alert-info shadow-lg">
    <div>
        <AlertInfo />
        <slot />
    </div>
</div>
