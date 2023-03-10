<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { SimplePool } from 'nostr-tools';
    import { encodeNpub } from "$lib/nostr/utils";
    import type { UserResume } from "$lib/types/user";
    import { subscribeResumes, subscribeMetadata, closePool } from "$lib/services/nostr";
    import Loading from "$lib/components/Loading.svelte";

    const QUERY_BATCH_SIZE = 100;
    const CHECK_METADATA_DELAY = 1000;

    export let onView = (r: UserResume, n: string, p: string) => {};

    let pool = new SimplePool();

    let checkMetadataTimer: ReturnType<typeof setTimeout> | null = null;

    let resumes: {[pubkey: string]: {resume: UserResume, createdAt: number}} = {};
    let metadataRequested: string[] = [];
    let metadata: {[pubkey: string]: {name: string, picture: string}} = {};

    function checkMetadataPeriodically() {
        let pubkeysToQuery: string[] = [];

        let i = 0;

        for (const pubkey of Object.keys(resumes)) {
            if (!(pubkey in metadata) && metadataRequested.indexOf(pubkey) === -1) {
                pubkeysToQuery.push(pubkey);
                i++;

                if (i == QUERY_BATCH_SIZE) {
                    break;
                }
            }
        }

        if (pubkeysToQuery.length !== 0) {
            metadataRequested = [...metadataRequested, ...pubkeysToQuery];
            subscribeMetadata(pool, pubkeysToQuery,
                (pk, m) => {
                    if (!(pk in metadata)) {
                        metadata[pk] = {name: m.name, picture: m.picture};
                    } else if (m.name !== undefined) {
                        metadata[pk].name = m.name;
                    } else if (m.picture !== undefined) {
                        metadata[pk].picture = m.picture;
                    }
            });
        }

        checkMetadataTimer = setTimeout(checkMetadataPeriodically, CHECK_METADATA_DELAY);
    }

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

        checkMetadataPeriodically();
    });

    onDestroy(async () => {
        if (checkMetadataTimer) {
            clearTimeout(checkMetadataTimer);
        }
        await closePool(pool);
    })
</script>

<div class="mx-auto w-full">
    {#if Object.keys(resumes).length == 0}
        <Loading />
    {:else}
        <div class="w-full p-2">
            {#each Object.entries(resumes) as [pubkey, r]}
                <div class="card bg-base-300 shadow-xl mt-4">
                    <figure>
                        <img src={pubkey in metadata ? metadata[pubkey].picture : null} alt="" />
                    </figure>
                    <div class="card-body">
                        <h2 class="card-title">{pubkey in metadata ? metadata[pubkey].name : encodeNpub(pubkey).substring(0, 10) + "..."}</h2>
                        <h3>{r.resume.jobTitle}</h3>
                        <div class="flex flex-row gap-2">
                            {#each r.resume.skills as skill}
                                <div class="badge badge-primary badge-lg mt-4">{skill.skill}</div>
                            {/each}
                        </div>
                        <p>{r.resume.bio}</p>
                        <div class="card-actions justify-end">
                            <button class="btn btn-primary" on:click={() => onView(r.resume, pubkey in metadata ? metadata[pubkey].name : null, pubkey in metadata ? metadata[pubkey].picture : null)}>View</button>
                            <a class="btn btn-primary" href="https://snort.social/p/{encodeNpub(pubkey)}" target="_blank" rel="noreferrer">Contact</a>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>