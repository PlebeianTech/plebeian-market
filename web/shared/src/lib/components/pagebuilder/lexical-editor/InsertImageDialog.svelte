<script lang="ts">
  import {
    CloseCircleButton,
    InsertImageUploadedDialogBody,
    InsertImageUriDialogBody,
    ModalDialog,
    getCommands,
    getEditor,
  } from '@bowline/svelte-lexical';

  export let showModal = false;
  export function open() {
    showModal = true;
  }

  $: if (!showModal) {
    mode = null;
  }

  let mode: null | 'url' | 'file' = null;

  const editor = getEditor();

  function closeDialog() {
    showModal = false;
    getCommands().FocusEditor.execute(editor);
  }
</script>

<ModalDialog bind:showModal>
  <CloseCircleButton on:click={() => (showModal = false)} />

  {#if !mode}
    <div class="w-64">
      <h2 class="Modal__title">Insert Image</h2>

      <div class="Modal__content">
        <div class="ToolbarPlugin__dialogButtonsList">
          <button
            class="Button__root"
            data-test-id="image-modal-option-url"
            on:click={() => (mode = 'url')}>
            URL
          </button>
          <button
            class="Button__root"
            data-test-id="image-modal-option-file"
            on:click={() => (mode = 'file')}>
            File
          </button>
        </div>
      </div>
    </div>
  {:else if mode === 'url'}
    <InsertImageUriDialogBody on:confirm={closeDialog} />
  {:else if mode === 'file'}
    <InsertImageUploadedDialogBody on:confirm={closeDialog} />
  {/if}
</ModalDialog>
