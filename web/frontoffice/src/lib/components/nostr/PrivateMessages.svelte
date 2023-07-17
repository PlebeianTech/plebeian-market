<script lang="ts">
    import EmailIcon from "$sharedLib/components/icons/Email.svelte";
    import {NostrPublicKey, privateMessages} from "$sharedLib/stores";
    import {getPrivateMessages, subscribeMetadata} from "$lib/services/nostr";
    import {decode} from "light-bolt11-decoder";
    import { goto } from "$app/navigation";

    let unreadConversations = 0;

    $: {
        // We need to "listen" for "human" so this
        // is called reactively when modifications
        // are done to messages or sections
        const reactivity = $privateMessages.human;
        vitamineHumanConversations();
    }

    export function vitamineHumanConversations() {
        // Calculating unread messages
        unreadConversations = 0;

        for (const [conversationPubkey, conversation] of Object.entries($privateMessages.human)) {
            let maxTimestamp = 0;
            let unreadMessages = 0;

            for (const message of conversation.messages) {
                if (message.created_at > maxTimestamp) {
                    maxTimestamp = message.created_at;
                }

                let messagesStorageJson = localStorage.getItem('readMessages');
                let messagesStorage = JSON.parse(messagesStorageJson) ?? {};
                let recordedMaxTimestamp = messagesStorage[conversationPubkey] ?? 0;

                if (message.created_at > recordedMaxTimestamp) {
                    unreadMessages++;
                }
            }

            if (unreadMessages > 0) {
                unreadConversations++;
            }

            conversation.maxTimestamp = maxTimestamp;
            conversation.unreadMessages = unreadMessages;
        }

        $privateMessages.unreadConversations = unreadConversations;

        // We need this so reactive blocks in messages/+page.svelte
        // can run again after this function updated unreadMessages
        $privateMessages.human = $privateMessages.human;
    }

    export async function getNostrDMs() {
        await getPrivateMessages($NostrPublicKey,
            (privateMessage) => {
                if (privateMessage !== null && typeof privateMessage === 'object') {
                    if (privateMessage.contentType === 'json') {
                        let type;

                        if (privateMessage['type'] !== undefined) {
                            type = Number(privateMessage.type);
                        } else {
                            // Workaround until NostrMarket adds the "type" property
                            if (privateMessage.paid) {
                                type = 2;
                            } else if (privateMessage.payment_options) {
                                type = 1;
                            } else {
                                type = 0;
                            }
                        }

                        privateMessage.type = type;

                        if (type === 1) {
                            for (const paymentOption of privateMessage.payment_options) {
                                if (paymentOption.type === 'ln') {
                                    const decodedInvoice = decode(paymentOption.link);

                                    paymentOption.amount_sats =
                                        decodedInvoice.sections.filter((section) => {
                                            return section.name === 'amount'
                                        })[0].value / 1000;

                                    paymentOption.expiry = decodedInvoice.expiry;
                                }
                            }
                        }

                        if (type === 10) {
                            privateMessage.isAuction = true;
                        }

                        let orderId = privateMessage.id;

                        if (orderId === undefined) {
                            return;
                        }

                        if (orderId in $privateMessages.automatic) {
                            // We need to merge objects because some properties
                            // are the same in different types like "message",
                            // but we want to have the last one

                            if (
                                ((privateMessage.type > $privateMessages.automatic[orderId].type) && privateMessage.type !== 10)
                                ||
                                (privateMessage.type === $privateMessages.automatic[orderId].type && privateMessage.created_at > $privateMessages.automatic[orderId].created_at)
                            ) {

                                $privateMessages.automatic[orderId] = {...$privateMessages.automatic[orderId], ...privateMessage};
                            } else {
                                $privateMessages.automatic[orderId] = {...privateMessage, ...$privateMessages.automatic[orderId]};
                            }

                        } else {
                            $privateMessages.automatic[orderId] = privateMessage;
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
                            for (const message of $privateMessages.human[pubKey].messages) {
                                if (privateMessage.id === message.id) {
                                    includeMessage = false;
                                }
                            }

                            if (includeMessage) {
                                $privateMessages.human[pubKey].messages.push(privateMessage);
                            }

                        } else {
                            $privateMessages.human[pubKey] = {
                                messages: [privateMessage]
                            };
                        }

                        // This is needed to fire reactivity when a new message arrives
                        $privateMessages.human = $privateMessages.human;
                    }
                }
            },
            getMetadataForHumanPubkeys
        );
    }

    export async function getMetadataForHumanPubkeys() {
        subscribeMetadata(Object.keys($privateMessages.human),
            (pubKey, m) => {
                if (m.name !== undefined) {
                    $privateMessages.human[pubKey].name = m.name;
                }
                if (m.picture !== undefined) {
                    $privateMessages.human[pubKey].picture = m.picture;
                }
            });
    }

    function gotoMessages() {
        goto('/messages')
    }

    $: if ($NostrPublicKey) {
        getNostrDMs();
    }
</script>

<div class="indicator" on:click={gotoMessages}>
    <div class="w-8 h-8">
        <EmailIcon />
    </div>

    {#if $NostrPublicKey}
        {#if unreadConversations}
            <div class="tooltip tooltip-bottom tooltip-error" data-tip="{unreadConversations} unread conversations">
                <span class="indicator-item badge badge-sm badge-error">
                    {unreadConversations}
                </span>
            </div>
        {/if}
    {:else}
        <div class="tooltip tooltip-bottom tooltip-secondary" data-tip="Login clicking here">
            <span class="indicator-item badge badge-sm badge-secondary">!</span>
        </div>
    {/if}
</div>
