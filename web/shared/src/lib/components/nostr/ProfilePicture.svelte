<script lang="ts">
    import {NostrPublicKey} from "$sharedLib/stores";
    import {subscribeMetadata} from "$sharedLib/services/nostr";
    import profilePicturePlaceHolder from "$sharedLib/images/profile_picture_placeholder.svg";

    let profileImage = null;

    $: if ($NostrPublicKey) {
        let gotProfile = false;

        subscribeMetadata([$NostrPublicKey],
            (_pk, metadata) => {
                if (gotProfile) {
                    return;
                }

                gotProfile = true;

                if (metadata.picture) {
                    profileImage = metadata.picture;
                }
            });
    }
</script>

{#if $NostrPublicKey}
    <label role="button" tabindex="0" class="btn btn-ghost btn-circle avatar hidden lg:block">
        <img class="w-10 rounded-full" src={profileImage ?? profilePicturePlaceHolder} alt="Avatar" />
    </label>
{/if}
