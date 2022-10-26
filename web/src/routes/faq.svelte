<svelte:head>
    <title>FAQ</title>
</svelte:head>

<script>
</script>

<div class="flex justify-center items-center md:mb-20">
    <div class="mt-10 ml-4 w-3/4">
        <h1 class="mt-5 text-4xl">Frequently Asked Questions</h1>
        <p class="mt-3 text-2xl">Q: How do I place a bid?</p>
        <p class="mt-1 text-s">A: Scan a QR code using your lightning wallet to place a bid. Bidding on an auction costs 21 sats. These sats will go directly to funding open-source initiatives such as <a href="https://opensats.org">OpenSats.</a></p>
        <p class="mt-3 text-2xl">Q: Do you take a percentage?</p>
        <p class="mt-1 text-s">A: We are built on the Value4Value model. When a seller creates a profile they have the option to donate up to 5% of the sale price to support Plebeian Market. When a buyer wins an auction, they are asked to send this donation to Plebeian Market before they are connected to the seller to complete the transaction. For example, if you win an auction and the winning bid is 1000 sats and the buyer has opted to donate 2.5%, you will be prompted to send us the 25 sats donation before being connected with the seller to pay the remaining 975 sats.</p>
        <p class="mt-3 text-2xl">Q: Why do you ask for a Twitter account?</p>
        <p class="mt-1 text-s">A: Eventually, we aim to use a DID (Decentralized ID) reputation system built on lightning, but for now Twitter is a good anchor and provides "proof of human." We don't pull any information from your Twitter account except for your profile picture and the images for your auction. Bitcoin Twitter has a huge network effect and will help you sell your listing!</p>
        <p class="mt-3 text-2xl">Q: Is Plebeian Market open source?</p>
        <p class="mt-1 text-s">A: We are 100% FOSS. By using Plebeian Market not only are you supporting its continued development but you're also supporting other FOSS (free open source software) projects in the Bitcoin community.</p>
        <p class="mt-3 text-2xl">Q: Where can I share my question or feedback?</p>
        <p class="mt-1 text-s">A: You can find us on <a class="link" href="https://t.me/PlebeianMarket">Telegram</a> or email us at <a class="link" href="email:support@plebeian.market">support@plebeian.market</a>. If you have a more technical feedback or would like to contribute to the development, you can find us on <a class="link" href="https://github.com/PlebeianTech/plebeian-market">GitHub</a>.</p>
        <p class="mt-3 text-2xl">Q: What about shipping?</p>
        <p class="mt-1 text-s">A: When you create a listing you can specify where you are shipping from. As a buyer, if you need additional information about the shipping cost for a specific listing, please reach out to the author of that listing directly.</p>
        <p class="mt-3 text-2xl">Q: Do you hold the funds in escrow?</p>
        <p class="mt-1 text-s">A: We do not touch the money at any point in the transaction, we simply run the auction to help you find the market value. The winner is put in contact with the seller and the two complete the payment directly. In the future we may develop an escrow system that does not require a trusted third party, such as a multisig Bitcoin escrow with a security deposit to protect buyer and seller, but we do not intend to ever be the trusted third party or hold the funds at any point during the transaction.</p>
        <p class="mt-3 text-2xl">Q: Plebeian?</p>
        <p class="mt-1 text-s">A: Everything about this project is designed by plebs for plebs.</p>
        <p class="mt-3 text-2xl">Q: I scanned the login QR code with my favorite lightning wallet and it gave me an error message! What can I do?</p>
        <p class="mt-1 text-s">A: Let them know that their app doesn't work for <a class="link" href="https://lightninglogin.live/learn">LNURL-auth</a>! Hopefully they will add support for this amazing feature. In the meantime you can use one of the wallets we have tested, such as <a class="link" href="https://breez.technology/">Breez</a>, <a class="link" href="https://phoenix.acinq.co/">Phoenix</a> or <a class="link" href="https://zeusln.app/">Zeus</a> on your mobile device, or <a class="link" href="https://getalby.com/">Alby</a> or <a class="link" href="https://thunderhub.io/">Thunderhub</a> on your computer. You can also use any <a class="link" href="https://github.com/fiatjaf/lnurl-rfc#lnurl-documents" target="_blank">LNURL-auth compatible wallet (see number 04).</a>
        <p class="mt-3 text-2xl">Q: How do I get the XPUB/YPUB/ZPUB from my wallet?</p>
        <p class="mt-1 text-s">A: Check this wonderful article by the Swan team on <a class="link" href="https://help.swanbitcoin.com/hc/en-us/articles/360056809674-Where-do-I-find-the-extended-public-key-xpub-ypub-zpub-of-my-wallet-">where to find the extended public key</a> for the most popular wallets.</p>
        <p class="mt-3 text-2xl">Q: What kind of software license is this project using?</p>
        <p class="mt-1 mb-5 text-s">A: This project has been initially released under the <a class="link" href="https://github.com/PlebeianTech/plebeian-market/blob/master/LICENSE.md">GNU General Public License (GPL)</a>. Once we have completed the MVPs for the other components of the ecosystem we will transition to a more permissive license, most likely MIT.</p>
    </div>
</div>