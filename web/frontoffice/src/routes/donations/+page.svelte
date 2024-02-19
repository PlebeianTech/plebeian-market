<script lang="ts">
    import Titleh1 from "$sharedLib/components/layout/Title-h1.svelte";
</script>

<svelte:head>
    <title>Support Us</title>
    <script src="https://embed.twentyuno.net/js/app.js"></script>
</svelte:head>

<Titleh1>Support Us</Titleh1>

<div class="grid justify-center items-center lg:mx-20 gap-6 lg:gap-20 place-content-center">
    <div>
        <p class="p-8 pt-3 pb-12 text-xl">If you like this project, consider making a donation to support us.</p>

        <lightning-widget
                name="Plebeian Market"
                accent="#ff3fb4"
                to="plebeianmarket@getalby.com"
                image="https://pbs.twimg.com/profile_images/1752669076269203456/JTFV9-8Q_400x400.png"
                amounts="10000,100000,1000000"
        />
    </div>
</div>
