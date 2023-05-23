<script lang="ts">
    import { sendMessage } from "$lib/services/nostr";
    import { getChannelIdForStallOwner, pmChannelNostrRoomId } from '$lib/nostr/utils'
    import { Info, user, NostrPool } from "$lib/stores";

    export let pmURL: string | null;

    let nostrRoomId;
    let message: string;
    let textConfirmationVisible: boolean;

    function getNostrTextModal(location: 'stall' | 'mktSquare' | 'nostrFeed') {
        switch (location) {
            case 'stall':
                message = 'Hi people! I just listed a new product. Give it a look:';
                nostrRoomId = getChannelIdForStallOwner($user);
                break;
            case 'mktSquare':
                message = 'Hey! Check the new product I just listed!';
                nostrRoomId = pmChannelNostrRoomId;
                break;
            case 'nostrFeed':
                message = 'Check the product I just published at Plebeian Market!';
                nostrRoomId = false;
                break;
        }

        message += '\n' + pmURL;

        textConfirmationVisible = true;
    }

    async function postToNostr() {
        if (message && message !== '') {
            sendMessage(message, nostrRoomId, null,
                () => {
                    textConfirmationVisible = false;
                    Info.set("¡Published to Nostr!");
            });
        }
    }
</script>

<div class="dropdown">
    <label tabindex="0" class="btn btn-secondary align-middle mb-2">
        <svg xmlns="http://www.w3.org/2000/svg"
             class="w-7 h-7 -ml-1 mr-2" viewBox="0 0 472.000000 528.000000"
             preserveAspectRatio="xMidYMid meet">
            <g transform="translate(0.000000,528.000000) scale(0.100000,-0.100000)"
               fill="#cfd4d4" stroke="none">
                <path d="M3960 5223 c-150 -57 -210 -357 -110 -553 55 -108 159 -219 311 -333
98 -74 157 -138 191 -205 20 -42 23 -61 23 -172 0 -146 -14 -188 -90 -269 -41
-44 -129 -96 -194 -116 -32 -10 -150 -8 -226 4 -45 6 -74 5 -115 -6 -83 -22
-115 -13 -252 70 -280 169 -387 200 -693 201 -329 1 -486 -43 -955 -272 -393
-191 -401 -193 -705 -200 -115 -2 -218 -8 -227 -13 -25 -13 -22 -40 7 -83 30
-44 25 -60 -13 -40 -15 7 -31 14 -36 14 -5 0 -17 7 -27 15 -28 26 -139 38
-234 26 -147 -20 -291 -96 -396 -208 -61 -65 -95 -120 -136 -218 -35 -87 -42
-139 -18 -149 8 -3 52 13 97 34 73 36 138 51 138 34 0 -4 -14 -50 -31 -103
-43 -134 -33 -211 28 -211 17 0 46 21 92 68 88 87 120 112 143 112 22 0 23
-19 3 -67 -19 -45 -30 -141 -21 -177 9 -37 42 -34 117 14 107 67 200 103 308
121 36 5 86 17 109 26 62 22 113 12 180 -35 127 -89 331 -169 591 -232 69 -16
129 -34 134 -39 6 -6 -3 -27 -22 -55 -32 -46 -177 -198 -241 -252 -103 -87
-172 -135 -225 -159 -119 -52 -174 -109 -191 -200 -5 -22 -9 -43 -10 -47 -1
-5 -2 -12 -3 -17 0 -4 -40 -63 -88 -129 -49 -67 -173 -243 -277 -392 -104
-149 -202 -281 -217 -294 -16 -13 -48 -27 -71 -31 -84 -14 -144 -44 -192 -94
-49 -53 -62 -86 -52 -127 6 -21 11 -25 29 -19 12 4 35 9 52 12 25 5 28 4 18
-8 -25 -30 -86 -147 -104 -198 -37 -106 -17 -247 34 -239 15 2 27 19 45 62 33
84 71 136 191 261 59 61 124 139 145 175 88 147 274 403 527 725 141 180 137
177 219 219 75 38 124 95 143 164 10 39 22 52 87 101 41 31 85 63 97 71 12 8
82 60 155 116 118 90 145 105 238 138 58 21 115 42 127 48 13 6 26 9 29 5 9
-8 -15 -66 -36 -92 -10 -11 -40 -79 -69 -151 -54 -139 -62 -190 -37 -247 40
-94 118 -108 231 -40 39 22 79 43 90 46 31 8 404 124 560 174 248 79 307 85
320 30 5 -23 13 -73 14 -93 2 -21 54 -64 77 -64 26 0 28 4 24 71 -1 27 3 50
10 54 7 5 38 -19 80 -61 102 -102 200 -151 216 -109 8 21 -6 48 -106 204 -117
183 -133 205 -176 237 -34 26 -45 29 -118 29 -73 -1 -107 -9 -361 -88 -154
-49 -311 -99 -350 -112 -138 -46 -245 -77 -255 -73 -5 1 13 38 41 81 36 57 63
86 95 105 77 46 144 102 144 120 0 10 10 28 23 40 20 19 35 22 106 22 95 0
336 25 431 44 158 33 335 129 431 234 96 105 130 212 134 419 1 99 6 147 15
158 7 9 54 40 104 69 280 165 425 318 533 562 89 201 80 434 -24 619 -40 73
-143 173 -295 288 -123 94 -165 151 -153 209 8 33 25 44 116 69 55 15 102 19
238 19 94 0 172 4 175 9 9 14 -14 28 -76 46 -80 23 -82 35 -6 35 67 0 91 8 80
27 -4 6 -74 32 -157 58 -120 38 -166 58 -234 102 -47 31 -100 62 -118 69 -32
14 -124 18 -153 7z"/>
            </g>
        </svg>
        Share on Nostr
    </label>
    <ul tabindex="0" class="dropdown-content menu p-2 shadow bg-secondary rounded-box w-72">
        <li><a href="#anchorId" on:click|preventDefault={() => getNostrTextModal("stall")}>My Stall</a></li>
        <li><a href="#anchorId" on:click|preventDefault={() => getNostrTextModal("mktSquare")}>Market Square</a></li>
        <li><a href="#anchorId" on:click|preventDefault={() => getNostrTextModal("nostrFeed")}>Public Nostr</a></li>
    </ul>
</div>

<!-- Nostr text confirmation Modal -->
<input type="checkbox" id="nostrTextConfirmation" class="modal-toggle" bind:checked={textConfirmationVisible}/>
<div class="modal">
    <div class="modal-box relative">
        <label for="nostrTextConfirmation" class="btn btn-sm btn-circle absolute right-2 top-2">✕</label>
        <h3 class="text-lg font-bold">Sharing this on Nostr:</h3>
        <textarea class="textarea textarea-secondary textarea-bordered textarea-md w-full max-w-md" bind:value={message}></textarea>
        <div class="modal-action justify-center">
            <button class="btn btn-secondary" on:click|preventDefault={postToNostr}>Publish</button>
        </div>
    </div>
</div>
