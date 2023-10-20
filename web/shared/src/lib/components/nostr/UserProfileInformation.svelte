<script lang="ts">
    import { browser } from "$app/environment";
    import {filterTags} from "$sharedLib/nostr/utils";
    import {getBadgeDefinitions, getBadgeAward, getProfileBadges, subscribeMetadata} from "$sharedLib/services/nostr";

    export let userPubkey: string = null;
    export let profile = null;

    export let badgesAwarded = [];
    export let badgesAccepted = [];
    export let profileBadgesLastEvent;
    export let badgeDefinitions = new Map<string, object>();
    export let pm_badges;
    export let other_badges;

    export let externalIdentities = [];
    export let verifyIdentities;

    $: if (browser && userPubkey) {
        getUserProfileInformation(userPubkey);
    }

    export function getUserProfileInformation(userPubkey: string) {
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
                if (externalIdentities.length > 0) {
                    await verifyIdentities();
                }
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
                // console.log('------- BadgeDefinition', badgeDefinition);

                const badgeObject = Object.fromEntries(badgeDefinition.tags);

                badgeObject.badgeFullName = badgeFullName;
                badgeObject.eventId = badgeEvent.id;        // Event ID from the "Badge Award"

                if (badgeDefinition.pubkey === '76cc29acb8008c68b105cf655d34de0b1f7bc0215eaae6bbc83173d6d3f7b987') {
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
