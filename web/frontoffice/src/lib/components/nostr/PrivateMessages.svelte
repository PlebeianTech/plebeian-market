<script lang="ts">
    import EmailIcon from "$sharedLibComponents/icons/Email.svelte";
    import {NostrPublicKey, privateMessages, NostrPool} from "$lib/stores";
    import {getPrivateMessages, subscribeMetadata} from "$lib/services/nostr";
    import {decode} from "light-bolt11-decoder";
    import { goto } from "$app/navigation";

    export async function getNostrDMs() {
        await getPrivateMessages($NostrPool, $NostrPublicKey,
            (privateMessage) => {
                if (privateMessage !== null && typeof privateMessage === 'object') {
                    if (privateMessage.contentType === 'json') {
                        let orderId = privateMessage.id;

                        let type;

                        if (privateMessage.type) {
                            type = Number(privateMessage.type);
                            privateMessage.type = type;
                        } else {
                            // Workaround until NostrMarket adds the "type" property
                            if (privateMessage.payment_options) {
                                type = 1;
                            } else if (privateMessage.paid) {
                                type = 2;
                            } else {
                                type = 0;
                            }
                        }

                        if (type === 1) {
                            for (const paymentOption of privateMessage.payment_options) {
                                if (paymentOption.type === 'ln') {
                                    const decodedInvoice = decode(paymentOption.link);

                                    paymentOption.amount =
                                        decodedInvoice.sections.filter((section) => {
                                            return section.name === 'amount'
                                        })[0].value / 1000;

                                    paymentOption.expiry = decodedInvoice.expiry;
                                }
                            }
                        }

                        if (privateMessage.created_at === 1682150218) {
                            // Uncomment to get a "Not shipped yet"
//                            return;
                        }

                        if (orderId in $privateMessages.automatic) {
                            // Because some properties are the same in different types
                            // like "message"
                            if (privateMessage.created_at > $privateMessages.automatic[orderId].created_at) {
                                $privateMessages.automatic[orderId] = {...$privateMessages.automatic[orderId], ...privateMessage};
                            } else {
                                $privateMessages.automatic[orderId] = {...privateMessage, ...$privateMessages.automatic[orderId]};
                            }

                            $privateMessages.automatic[orderId].type = type;

                        } else {
                            $privateMessages.automatic[orderId] = privateMessage;

                            if (!privateMessage.type) {
                                $privateMessages.automatic[orderId].type = type;
                            }
                        }

                        // This is needed to fire reactivity when a new message arrives
                        $privateMessages.automatic[orderId] = $privateMessages.automatic[orderId];
                    } else {
                        // "Human" messages
                        let pubKey = privateMessage.pubkey;

                        if (pubKey === $NostrPublicKey) {
                            // This is a message of mine. What conversation does it belong to?
                            pubKey = privateMessage.sender;
                        }

                        if (pubKey in $privateMessages.human) {
                            let includeMessage = true;
                            for (const message of $privateMessages.human[pubKey]) {
                                if (privateMessage.id === message.id) {
                                    includeMessage = false;
                                }
                            }

                            if (includeMessage) {
                                $privateMessages.human[pubKey].push(privateMessage);
                            }

                        } else {
                            $privateMessages.human[pubKey] = [privateMessage];
                        }

                        // This is needed to fire reactivity when a new message arrives
                        $privateMessages.human[pubKey] = $privateMessages.human[pubKey];
                    }
                }
            },
            getMetadataForHumanPubkeys
        );
    }

    export async function getMetadataForHumanPubkeys() {
        subscribeMetadata($NostrPool, Object.keys($privateMessages.human),
            (pubKey, m) => {
                if (m.name !== undefined) {
                    $privateMessages.human[pubKey].name = m.name;
                }
                if (m.picture !== undefined) {
                    $privateMessages.human[pubKey].picture = m.picture;
                }
            });
    }

    $: if ($NostrPublicKey) {
        getNostrDMs();
    }
</script>

<div class="btn btn-ghost btn-circle" on:click={() => goto('/messages')}>
    <div class="indicator">
        <div class="w-8 h-8">
            <EmailIcon />
        </div>

        {#if $NostrPublicKey}
            <span class="indicator-item badge badge-sm" class:badge-error={Object.entries($privateMessages.human ?? []).length > 0}>
                {Object.entries($privateMessages.human ?? []).length}
            </span>
        {:else}
            <span class="indicator-item badge badge-sm badge-secondary">!</span>
        {/if}
    </div>
</div>
