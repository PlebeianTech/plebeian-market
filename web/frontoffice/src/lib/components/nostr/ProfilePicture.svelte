<script lang="ts">
    import {NostrPublicKey} from "../../stores";
    import {subscribeMetadata} from "../../services/nostr";

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

{#if $NostrPublicKey && profileImage}
    <label role="button" for={null} tabindex="0" class="btn btn-ghost btn-circle avatar hidden lg:block ml-2">
        <img class="w-10 rounded-full" src={profileImage} alt="Avatar" />
    </label>
{/if}
