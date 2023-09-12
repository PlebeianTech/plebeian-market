<script lang="ts">
    import {page} from "$app/stores";
    import {onMount} from "svelte";

    export let role: string;

    let question: string = '';

    onMount(() => {
        question = $page.url.searchParams.get('question');
    });
</script>

<div class="flex justify-center items-center md:mb-20 p-2">
    <div class="lg:w-2/3 space-y-6">
        <div class="collapse">
            <input type="checkbox" />
            <div class="collapse-title text-xl font-medium">General FAQ</div>
            <div class="collapse-content">
                <div class="collapse collapse-plus bg-base-300">
                    <input type="radio" />
                    <div class="collapse-title text-xl font-medium">
                        Do you take a percentage?
                    </div>
                    <div class="collapse-content">
                        <p>We are built on the Value4Value model. When a seller creates a profile, they have the option to donate up to 5% of the sale price to support Plebeian Market. When a buyer buys a product or wins an auction, they are asked to send this donation to Plebeian Market before they are connected to the seller to complete the transaction. For example, if you win an auction and the winning bid is 1000 sats and the seller has opted to donate 2.5%, you will be prompted to send us the 25 sats donation before being connected with the seller to pay the remaining 975 sats.</p>
                    </div>
                </div>

                <div class="collapse collapse-plus bg-base-300 mt-4">
                    <input type="radio" />
                    <div class="collapse-title text-xl font-medium">
                        Is Plebeian Market open source?
                    </div>
                    <div class="collapse-content">
                        <p>We are 100% FOSS. By using Plebeian Market not only are you supporting its continued development, but you're also supporting other FOSS (free open source software) projects in the Bitcoin community.</p>
                    </div>
                </div>

                <div class="collapse collapse-plus bg-base-300 mt-4">
                    <input type="radio" />
                    <div class="collapse-title text-xl font-medium">
                        What kind of software license is this project using?
                    </div>
                    <div class="collapse-content">
                        <p>This project has been initially released under the <a class="link" target="_blank" href="https://github.com/PlebeianTech/plebeian-market/blob/master/LICENSE.md">GNU General Public License (GPL)</a>. Once we have completed the MVPs for the other components of the ecosystem we will transition to a more permissive license, most likely MIT.</p>
                    </div>
                </div>

                <div class="collapse collapse-plus bg-base-300 mt-4">
                    <input type="radio" />
                    <div class="collapse-title text-xl font-medium">
                        Where can I share my question or feedback?
                    </div>
                    <div class="collapse-content">
                        <p>You can find us on <a class="link" target="_blank" href="https://t.me/PlebeianMarket">Telegram</a> or email us at <a class="link" target="_blank" href="email:support@plebeian.market">support@plebeian.market</a>. If you have a more technical feedback or would like to contribute to the development, you can find us on <a class="link" target="_blank" href="https://github.com/PlebeianTech/plebeian-market">GitHub</a>.</p>
                    </div>
                </div>

                <div class="collapse collapse-plus bg-base-300 mt-4">
                    <input type="radio" />
                    <div class="collapse-title text-xl font-medium">
                        Plebeian?
                    </div>
                    <div class="collapse-content">
                        <p>Everything about this project is designed by plebs for plebs.</p>
                    </div>
                </div>

                <div class="collapse collapse-plus bg-base-300 mt-4">
                    <input type="radio" />
                    <div class="collapse-title text-xl font-medium">
                        Do you hold the funds in escrow?
                    </div>
                    <div class="collapse-content">
                        <p>We do not touch the money at any point in the transaction, we simply run the auction to help you find the market value. The winner is put in contact with the seller and the two complete the payment directly. In the future we may develop an escrow system that does not require a trusted third party, such as a multisig Bitcoin escrow with a security deposit to protect buyer and seller, but we do not intend to ever be the trusted third party or hold the funds at any point during the transaction.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="collapse">
            <input type="checkbox" checked={role === 'buyer'} />
            <div class="collapse-title text-xl font-medium">Buyer FAQ</div>
            <div class="collapse-content">
                <div class="collapse collapse-plus bg-base-300">
                    <input type="radio" />
                    <div class="collapse-title text-xl font-medium">
                        How do I place a bid?
                    </div>
                    <div class="collapse-content">
                        <p class="text-s">Scan a QR code using your lightning wallet to place a bid. Bidding on an auction costs 21 sats. These sats will go directly to funding open-source initiatives such as <a target="_blank" href="https://opensats.org">OpenSats</a>.</p>
                    </div>
                </div>
                <div class="collapse collapse-plus bg-base-300 mt-4">
                    {(console.log('question', question), '')}
                    <input type="radio" checked={question === 'howToGetPMBadge'} />
                    <div class="collapse-title text-xl font-medium">
                        How do I get a Plebeian Market badge?
                    </div>
                    <div class="collapse-content">
                        <p class="text-s">There are 3 ways to get a PM badge:</p>
                    </div>
                </div>
                <div class="collapse collapse-plus bg-base-300 mt-4">
                    <input type="radio" />
                    <div class="collapse-title text-xl font-medium">
                        How does the shipping works?
                    </div>
                    <div class="collapse-content">
                        <p>You'll be able to see the shipping options and cost for each stall in the Stall Browser. Also, you'll be able to see and choose a shipping option during the checkout process. If you need additional information about the shipping cost for a specific listing, please reach out to the merchant of that listing directly using the <b>Contact the merchant</b> button available in the stall.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="collapse">
            <input type="checkbox" checked={role === 'seller'} />
            <div class="collapse-title text-xl font-medium">Seller FAQ</div>
            <div class="collapse-content">
                <div class="collapse collapse-plus bg-base-300">
                    <input type="radio" checked={question === 'xpub'} />
                    <div class="collapse-title text-xl font-medium">
                        How do I get the XPUB/YPUB/ZPUB from my wallet?
                    </div>
                    <div class="collapse-content">
                        <p>Check this wonderful article by the Swan team on <a class="link" target="_blank" href="https://help.swanbitcoin.com/hc/en-us/articles/360056809674-Where-do-I-find-the-extended-public-key-xpub-ypub-zpub-of-my-wallet-">where to find the extended public key</a> for the most popular wallets. We don't recommend using Muun, Breez or Phoenix because those are lightning wallets that support on-chain capabilities through some tricks, and we've had problems with them in the past.</p>
                    </div>
                </div>

                <div class="collapse collapse-plus bg-base-300 mt-4">
                    <input type="radio" />
                    <div class="collapse-title text-xl font-medium">
                        How does the shipping work?
                    </div>
                    <div class="collapse-content">
                        <p>When you create (or edit) your stall, you can specify different options of places where you ship your products to, and the cost to ship the products there.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
