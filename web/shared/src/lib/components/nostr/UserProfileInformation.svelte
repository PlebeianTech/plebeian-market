<script lang="ts">
    import { browser } from "$app/environment";
    import {filterTags, pmStallPubkey} from "$sharedLib/nostr/utils";
    import {getBadgeDefinitions, getBadgeAward, getProfileBadges, subscribeMetadata} from "$sharedLib/services/nostr";

    export let userPubkey: string = null;
    export let profile = null;
    export let profileFinishedLoading = false;

    export let badgesAwarded = [];
    export let badgesAccepted = [];
    export let profileBadgesLastEvent;
    export let badgeDefinitions = new Map<string, object>();
    export let pm_badges;
    export let other_badges;

    export let externalIdentities = [];

    $: if (browser && userPubkey) {
        getUserProfileInformation(userPubkey);
    }

    export function getUserProfileInformation(userPubkey: string) {
        externalIdentities = [];
        profile = null;
        profileFinishedLoading = false;
        badgesAwarded = [];
        badgesAccepted = [];
        badgeDefinitions = new Map<string, object>();
        pm_badges = false;
        other_badges = false;

        subscribeMetadata([userPubkey],
            (pk, profileMeta) => {
                if (profile === null || profile.created_at < profileMeta.created_at) {
                    profile = profileMeta;

                    externalIdentities = [];

                    filterTags(profile.tags, 'i').forEach(externalIdentity => {
                        const externalIdentityToken: string = externalIdentity[1] + ':' + externalIdentity[2];

                        if (!externalIdentities.includes(externalIdentityToken)) {
                            externalIdentities.push(externalIdentityToken);
                            externalIdentities = externalIdentities;
                        }
                    });
                }
            },
            async () => {
                profileFinishedLoading = true;
            });

        getProfileBadges(userPubkey, (profileBadgeEvent) => {
            if (profileBadgesLastEvent === null || profileBadgesLastEvent.created_at < profileBadgeEvent.created_at) {
                getBadgeDefinition(profileBadgeEvent, true);
                profileBadgesLastEvent = profileBadgeEvent;
            }
        });

        getBadgeAward(userPubkey, (badgeAwardEvent) => {
            getBadgeDefinition(badgeAwardEvent, false);
        });
    }

    export function getBadgeDefinition(badgeEvent: object, isProfileBadge: boolean) {
        filterTags(badgeEvent.tags, 'a').forEach(tagId => {
            const badgeFullName = tagId[1];
            const badgeIDarray = badgeFullName.split(':');
            const badgeName: string = badgeIDarray[2];
            const badgeAuthor: string = badgeIDarray[1];

            getBadgeDefinitions(badgeName, badgeAuthor, (badgeDefinition) => {
                const badgeObject = Object.fromEntries(badgeDefinition.tags);

                badgeObject.badgeFullName = badgeFullName;
                badgeObject.eventId = badgeEvent.id;        // Event ID from the "Badge Award"

                if (badgeDefinition.pubkey === pmStallPubkey || badgeDefinition.id === "4a8891b6e8b65fe93d749600a2488df1a7c0c7e43a4b6fc46c4a145b03518506") {
                    badgeObject.pm_issued = true;
                    pm_badges = true;
                } else {
                    badgeObject.pm_issued = false;
                    other_badges = true;
                }


                if (!badgeDefinitions.get(badgeFullName)) {
                    if (isProfileBadge) {
                        badgeObject.accepted = isProfileBadge;
                    }

                    badgeDefinitions.set(badgeFullName, badgeObject);
                }

                if (isProfileBadge) {
                    if (!badgesAccepted.includes(badgeFullName)) {
                        badgesAccepted.push(badgeFullName);
                        badgesAccepted = badgesAccepted;
                    }
                } else {
                    if (!badgesAwarded.includes(badgeFullName)) {
                        badgesAwarded.push(badgeFullName);
                        badgesAwarded = badgesAwarded;
                    }
                }
            });
        });
    }
</script>
