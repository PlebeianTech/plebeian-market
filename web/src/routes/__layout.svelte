<script lang="ts">
    import { onDestroy } from 'svelte';
    import { toasts, ToastContainer }  from "svelte-toasts";
    import "../app.css";
    import { token, Info } from "../lib/stores";
    import Navbar from "../lib/components/Navbar.svelte";

    token.set(localStorage.getItem('token'));

	const unsubscribe = Info.subscribe(value => {
        if (value) {
            toasts.add({
                description: value,
                duration: 3000,
                placement: 'bottom-right',
                type: 'info'
            });
            Info.set(null);
        }
	});

	onDestroy(unsubscribe);
</script>

<div class="flex flex-col">
    <Navbar />
    <slot />
    <ToastContainer placement="bottom-right" let:data={data}>
        <div class="alert alert-info shadow-lg">
            <div>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              <span>{data.description}</span>
            </div>
          </div>
    </ToastContainer>
</div>
