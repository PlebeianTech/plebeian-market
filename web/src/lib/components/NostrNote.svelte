<script lang="ts">
    import {formatTimestamp} from '$lib/nostr/utils';
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg?url";

    export let message;
</script>

<div class="flex py-2" class:mt-0={message.samePubKey} class:mt-5={!message.samePubKey} class:profileInfo={!message.samePubKey} data-note-id="{message.id}">

  <!-- AVATAR -->
  <div class="">
    <div class="chat-image avatar">
        <div class="w-10 mx-4 rounded-full ring-primary ring-offset-base-100 ring-offset-1" class:ring={!message.samePubKey}>
            {#if !message.samePubKey}
                <img src="{message.profileImage ?? profilePicturePlaceHolder}" alt="profile picture" class:profileInfoImage={!message.samePubKey} />
            {/if}
        </div>
    </div>
  </div>

  <div class="items-center w-full border-b border-gray-600 px-4">
      <!-- NAME, BADGES, DATE -->
      <div class="space-y-1">
        {#if !message.samePubKey}
            <div class="chat-header flex items-center">
                <p class="mr-3" class:profileInfoName={!message.samePubKey}>{message.profileName ?? message.pubkey.slice(0, 8)}</p>
                {#if message.nip05verified}
                <div class="dropdown dropdown-bottom dropdown-hover dropdown-end">
                  <label tabindex="0" class="hover:cursor-pointer hover:scale-110 duration-300">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
                      <path fill-rule="evenodd" d="M8.603 3.799A4.49 4.49 0 0112 2.25c1.357 0 2.573.6 3.397 1.549a4.49 4.49 0 013.498 1.307 4.491 4.491 0 011.307 3.497A4.49 4.49 0 0121.75 12a4.49 4.49 0 01-1.549 3.397 4.491 4.491 0 01-1.307 3.497 4.491 4.491 0 01-3.497 1.307A4.49 4.49 0 0112 21.75a4.49 4.49 0 01-3.397-1.549 4.49 4.49 0 01-3.498-1.306 4.491 4.491 0 01-1.307-3.498A4.49 4.49 0 012.25 12c0-1.357.6-2.573 1.549-3.397a4.49 4.49 0 011.307-3.497 4.49 4.49 0 013.497-1.307zm7.007 6.387a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd" />
                    </svg>
                  </label>
                  <ul tabindex="0" class="dropdown-content translate-x-20">
                    <li>
                        <div class="badge badge-secondary text-xs whitespace-nowrap">{message.nip05}</div>
                    </li>
                  </ul>
                </div>
                {/if}
            </div>
        {/if}
        <div class="text-xs opacity-50">{formatTimestamp(message.created_at)}</div>
      </div>

      <div class="">
        <!-- MESSAGES AND ICONS -->
        <div>
          <div class="my-4">{@html message.content}</div>

          <!-- ICONS -->
          <div class="flex items-center w-full justify-between mb-2">
            <!-- REPOST -->
            <button class="btn btn-ghost tooltip tooltip-right" data-tip="repost">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
            </button>

            <!-- REPLY -->
            <button class="btn btn-ghost tooltip tooltip-right" data-tip="reply">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
              </svg>
            </button>

            <!-- LIKE -->
            <button class="btn btn-ghost tooltip tooltip-right" data-tip="like">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
              </svg>
            </button>

            <!-- EMBED -->
            <button class="btn btn-ghost tooltip tooltip-left" data-tip="embed">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
              </svg>
            </button>

          </div>
        </div>
      </div>
  </div>


</div>
