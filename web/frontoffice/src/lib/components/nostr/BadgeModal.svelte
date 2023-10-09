<script lang="ts">
    import badgeImageFallback from "$sharedLib/images/badge_placeholder.svg";
    import {nostrAcceptBadge} from "$sharedLib/services/nostr";
    import {Info, Error} from "$sharedLib/stores";

    export let onImgError = () => {};
    export let profileBadgesLastEvent;
    export let badgeInfo;
    export let myBadge = false;

    function acceptBadge() {
        if (badgeInfo.accepted) {
            Error.set('Badge already accepted!');
            console.error('This badge was already accepted');
            return;
        }

        if (profileBadgesLastEvent.tags.length < 3) {
            console.debug("nostrAcceptBadge - profile doesn't have a single entire badge");
            profileBadgesLastEvent.tags = [['d', 'profile_badges']];
        } else {
            console.debug("nostrAcceptBadge - adding new badge to profile");
        }

        profileBadgesLastEvent.tags.push(['a', badgeInfo.badgeFullName]);   // Adding "Badge Definition" key
        profileBadgesLastEvent.tags.push(['e', badgeInfo.eventId]);          // Adding "Badge Award" event id

        nostrAcceptBadge(profileBadgesLastEvent.tags, (badgeDefinition) => {
            Info.set("Badge accepted!");
            badgeInfo.accepted = true;
            window.badge_modal.close();
        });
    }
</script>

<dialog id="badge_modal" class="modal">
    {#if badgeInfo}
        <div class="modal-box w-11/12 max-w-3xl">
            <form method="dialog">
                <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
            </form>
            <div class="flex w-full">
                <div class="grid flex-grow place-items-center">
                    <figure class="avatar mask mask-squircle h-32 w-32 md:h-72 md:w-72">
                        <img id="badgeModalImg"
                             src={badgeInfo.image ?? badgeImageFallback}
                             alt=""
                             on:load={(event) => {event.srcElement.style.visibility="visible"}}
                             on:error={(event) => onImgError(event.srcElement)} />
                    </figure>
                </div>
                <div class="grid flex-grow place-items-center ml-4 md:ml-12">
                    <p class="font-bold text-xl md:text-2xl mb-3">{badgeInfo.name}</p>
                    <p class="text-lg md:text-xl align-top">{badgeInfo.description}</p>
                </div>
            </div>
            {#if myBadge && !badgeInfo.accepted}
                <div class="mt-8 grid flex-grow place-items-center">
                    <p>You have been awarded this badge. If you consider it valuable, <b>you can accept it to have it displayed on your profile</b>.</p>
                    <button class="btn btn-primary" on:click={acceptBadge}>Accept badge</button>
                </div>
            {/if}
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    {/if}
</dialog>