<script lang="ts">
    export let leftUsername: string;
    export let leftProfileImageUrl: string;
    export let rightUsername: string;
    export let rightProfileImageUrl: string;
</script>

<div class="bg-base-200 flex justify-center items-center max-w-full rounded py-2">
    <div class="text-center w-1/3">
        <div class="avatar">
            <div class="w-24 rounded-full">
                <img src={leftProfileImageUrl} alt="Avatar" />
            </div>
        </div>
        <p class="text-2xl ml-5">@{leftUsername}</p>
    </div>
    <div class="text-center text-6xl w-1/8">
        &#129309;
    </div>
    <div class="text-center w-1/3">
        <div class="avatar">
            <div class="w-24 rounded-full">
                <a href="https://twitter.com/{rightUsername}" target="_blank">
                    <img src={rightProfileImageUrl} alt="Avatar" />
                </a>
            </div>
        </div>
        <p class="text-2xl ml-5">
            <a href="https://twitter.com/{rightUsername}" target="_blank">
                @{rightUsername}
            </a>
        </p>
    </div>
</div>