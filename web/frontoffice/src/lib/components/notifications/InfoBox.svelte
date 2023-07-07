<script lang="ts">
    import AlertInfo from "$sharedLib/components/icons/AlertInfo.svelte";

    export let classText: string = '';
</script>
<div class="alert alert-info shadow-lg {classText}">
    <div>
        <AlertInfo />
        <span><slot /></span>
    </div>
</div>
