<script lang="ts">
    import type { IAccount } from "$lib/types/user";

    export let owner: IAccount | null;
    
    $: telegramUsername = owner ? owner.telegramUsername : null;
    $: telegramHref = owner && telegramUsername ? `https://t.me/${owner.telegramUsername}` : null;

    $: twitterUsername = owner ? owner.twitterUsername : null;
    $: twitterHref = owner && twitterUsername ? `https://twitter.com/${owner.twitterUsername}` : null;
</script>

<div class="lg:flex items-center lg:space-x-2">
  <!-- TELEGRAM -->
  {#if telegramHref}
      <a href={telegramHref} class="link text-2xl flex items-center space-x-2" target="_blank" rel="noreferrer">
          <span class="flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-telegram" viewBox="0 0 16 16">
                  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.287 5.906c-.778.324-2.334.994-4.666 2.01-.378.15-.577.298-.595.442-.03.243.275.339.69.47l.175.055c.408.133.958.288 1.243.294.26.006.549-.1.868-.32 2.179-1.471 3.304-2.214 3.374-2.23.05-.012.12-.026.166.016.047.041.042.12.037.141-.03.129-1.227 1.241-1.846 1.817-.193.18-.33.307-.358.336a8.154 8.154 0 0 1-.188.186c-.38.366-.664.64.015 1.088.327.216.589.393.85.571.284.194.568.387.936.629.093.06.183.125.27.187.331.236.63.448.997.414.214-.02.435-.22.547-.82.265-1.417.786-4.486.906-5.751a1.426 1.426 0 0 0-.013-.315.337.337 0 0 0-.114-.217.526.526 0 0 0-.31-.093c-.3.005-.763.166-2.984 1.09z"/>
              </svg>
          </span>
          <span class="flex items-center justify-center">
              @{telegramUsername}
          </span>
      </a>
  {/if}
  <!-- TWITTER -->
  {#if twitterHref}
    <a href={twitterHref} class="link text-2xl flex items-center space-x-2" target="_blank" rel="noreferrer">
        <span class="flex items-center justify-center">
            <svg width="24" height="24" viewBox="0 0 24 24" class="fill-current">
                <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"></path>
            </svg>
        </span>
        <span class="flex items-center justify-center">
            @{twitterUsername}
        </span>
    </a>
  {/if}            
</div>