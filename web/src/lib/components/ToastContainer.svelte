<!--
    This file is essentially the same as https://github.com/mzohaibqc/svelte-toasts/blob/main/src/ToastContainer.svelte
    with the only difference that "pointer-events" is set to "auto", which allows for clickable toasts!

    TODO: contribute back to the svelte-toasts library and get rid of this ugly override!
-->
<script>
    import { fly, fade } from 'svelte/transition';
    import { onMount } from 'svelte';
    import { flip } from 'svelte/animate';
    import { toasts } from 'svelte-toasts';
    /**
     * @typedef {'success' | 'info' | 'error' | 'warning'} ToastType
     * @typedef {'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'top-center' | 'bottom-center' | 'center-center'} Placement
     * @typedef {{
        uid: number;
        title?: string;
        description: string;
        duration: number;
        type: ToastType;
        theme?: Theme;
        placement: Placement;
        showProgress?: boolean;
        remove?: Function;
        update?: Function;
        onRemove?: Function;
        onClick?: Function;
      }} ToastProps
     */
    /**
     * Default theme for all toasts
     * @type { Theme }
     */
    export let theme = 'dark';
    /**
     * Default placement for all toasts
     * @type { Placement }
     */
    export let placement = 'bottom-right';
    /**
     * Default type of all toasts
     * @type { ToastType }
     */
    export let type = 'info';
    /**
     * Show progress if showProgress is true and duration is greater then 0
     * @type { boolean }
     */
    export let showProgress = false;
    /**
     * Default duration for all toasts to auto close. 0 to disable auto close
     * @type { number }
     */
    export let duration = 3000;
    /**
     * Width of all toasts
     * @type { string }
     */
    export let width = '320px';
    /**
     * Default slot which is Toast component/template which will get toast data
     * @slot {{ data: ToastProps }}
     */
    const placements = [
      'bottom-right',
      'bottom-left',
      'top-right',
      'top-left',
      'top-center',
      'bottom-center',
      'center-center',
    ];
    const flyMap = {
      'bottom-right': 400,
      'top-right': -400,
      'bottom-left': 400,
      'top-left': -400,
      'bottom-center': 400,
      'top-center': -400,
      'center-center': -800,
    };
    onMount(() => {
      toasts.setDefaults({
        placement,
        showProgress,
        theme,
        duration,
        type,
      });
    });
  </script>
  
  {#each placements as placement}
    <div class="toast-container {placement}" style="width: {width}">
      <ul>
        {#each $toasts
          .filter((n) => n.placement === placement)
          .reverse() as toast (toast.uid)}
          <li
            animate:flip
            out:fly={{ y: flyMap[toast.placement], duration: 1000 }}
            in:fade={{ duration: 500 }}
          >
            {#if toast.component}
              <svelte:component this={toast.component} data={toast} />
            {:else}
              <slot data={toast} />
            {/if}
          </li>
        {/each}
      </ul>
    </div>
  {/each}
  
  <style>
    ul {
      list-style: none;
      margin: 0;
      padding: 0;
    }
    li {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }
    .toast-container {
      z-index: 9999;
      position: fixed;
      padding: 4px;
      box-sizing: border-box;
      color: #fff;
      width: max-content;
      max-width: 100%;
      pointer-events: auto;
    }
    .toast-container.bottom-right {
      bottom: 1em;
      right: 1em;
    }
    .toast-container.bottom-left {
      bottom: 1em;
      left: 1em;
    }
    .toast-container.top-left {
      top: 1em;
      left: 1em;
    }
    .toast-container.top-right {
      top: 1em;
      right: 1em;
    }
    .toast-container.top-center {
      top: 1em;
      right: 50%;
      left: 50%;
      transform: translate(-50%, 0);
    }
    .toast-container.bottom-center {
      bottom: 1em;
      right: 50%;
      left: 50%;
      transform: translate(-50%, 0);
    }
    .toast-container.center-center {
      top: 50%;
      right: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }
    .toast-container > :not(:last-child) {
      margin-bottom: 10px;
    }
  </style>