<script lang="ts">
    import { onMount } from 'svelte';
    import { SimplePool } from 'nostr-tools';
    import { encodeNpub } from "$lib/nostr/utils";
    import type { UserResume } from "$lib/types/user";
    import { subscribeResumes } from "$lib/services/nostr";

    export let onView = (_: UserResume) => {};

    let pool = new SimplePool();

    let resumes: {[pubkey: string]: {resume: UserResume, createdAt: number}} = {};

    onMount(async () => {
        subscribeResumes(pool,
            (pk, r, rcAt) => {
                if (pk in resumes) {
                    if (resumes[pk].createdAt < rcAt) {
                        resumes[pk].resume = r;
                        resumes[pk].createdAt = rcAt;
                    }
                } else {
                    resumes[pk] = {resume: r, createdAt: rcAt};
                }
            });
    });
</script>

<div class="mx-auto w-full">
    <div class="overflow-x-auto w-full p-2">
        <table class="w-full">
            <thead class="bg-zinc-700/80">
                <th class="text-start text-blue-200 px-4 whitespace-nowrap py-4 text-sm">Nostr</th>
                <th class="text-start text-blue-200 px-4 whitespace-nowrap py-4 text-sm">Job title</th>
                <th class="text-start text-blue-200 px-4 whitespace-nowrap py-4 text-sm">Skills</th>
                <th class="text-start text-blue-200 px-4 whitespace-nowrap py-4 text-sm">Desired yearly salary (USD)</th>
                <th class="text-start text-blue-200 px-4 whitespace-nowrap py-4 text-sm">Hourly rate (USD)</th>
                <th class="text-start text-blue-200 px-4 whitespace-nowrap py-4 text-sm">Résumé</th>
            </thead>
            <tbody class="w-full whitespace-nowrap">
                {#each Object.entries(resumes) as [pubkey, r]}
                    <tr>
                        <td>
                            <a class="link" href="https://snort.social/p/{encodeNpub(pubkey)}">{encodeNpub(pubkey)}</a>
                        </td>
                        <td>
                            {r.resume.jobTitle}
                        </td>
                        <td class="flex flex-row gap-2">
                            {#each r.resume.skills as skill}
                                <div class="badge badge-primary badge-lg mt-4">{skill.skill}</div>
                            {/each}
                        </td>
                        <td>
                            {#if r.resume.desiredYearlySalaryUsd}
                                {r.resume.desiredYearlySalaryUsd}
                            {/if}
                        </td>
                        <td>
                            {#if r.resume.hourlyRateUsd}
                                {r.resume.hourlyRateUsd}
                            {/if}
                        </td>
                        <td>
                            <a class="link" href={null} on:click={() => onView(r.resume)}>View</a>
                        </td>
                </tr>
                {/each}
            </tbody>
        </table>
    </div>
</div>