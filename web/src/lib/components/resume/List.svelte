<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { SimplePool } from 'nostr-tools';
    import { encodeNpub } from "$lib/nostr/utils";
    import type { UserResume } from "$lib/types/user";
    import { subscribeResumes, subscribeMetadata, closePool } from "$lib/services/nostr";
    import Loading from "$lib/components/Loading.svelte";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";

    const QUERY_BATCH_SIZE = 100;
    const CHECK_METADATA_DELAY = 1000;

    export let onView = (r: UserResume, n: string | null, p: string | null) => {};

    let pool = new SimplePool();

    let checkMetadataTimer: ReturnType<typeof setTimeout> | null = null;

    let resumes: {[pubkey: string]: {resume: UserResume, createdAt: number}} = {};
    let metadataRequested: string[] = [];
    let metadata: {[pubkey: string]: {name: string, picture: string}} = {};

    let skills: {[skill: string]: number} = {};
    function addSkills(resume: UserResume, increment: -1 | 1) {
        for (const s of resume.skills) {
            if (!(s.skill in skills)) {
                skills[s.skill] = 1;
            } else {
                skills[s.skill] += increment;
            }
        }
    }

    let skillFilter: string | null = null;

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
                    } else {
                        if (m.name !== undefined) {
                            metadata[pk].name = m.name;
                        }
                        if (m.picture !== undefined) {
                            metadata[pk].picture = m.picture;
                        }
                    }
            });
        }

        checkMetadataTimer = setTimeout(checkMetadataPeriodically, CHECK_METADATA_DELAY);
    }

    onMount(async () => {
        subscribeResumes(pool,
            (pk, r, rcAt) => {
                if (pk in resumes) {
                    addSkills(resumes[pk].resume, -1);
                    if (resumes[pk].createdAt < rcAt) {
                        resumes[pk].resume = r;
                        resumes[pk].createdAt = rcAt;
                    }
                    addSkills(resumes[pk].resume, 1);
                } else {
                    resumes[pk] = {resume: r, createdAt: rcAt};
                    addSkills(resumes[pk].resume, 1);
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
    {#if Object.keys(resumes).length === 0}
        <Loading />
    {:else}
        <div class="flex gap-4">
            <div>
                <div class="badge badge-primary badge-lg mt-4 cursor-pointer" class:badge-outline={skillFilter !== null} on:click={() => skillFilter = null} on:keypress={() => skillFilter = null}>All</div>
            </div>
            {#each Object.entries(skills) as [skill, count]}
                <div>
                    <div class="badge badge-primary badge-lg mt-4 cursor-pointer z-0" class:badge-outline={skill !== skillFilter} on:click={() => {if (skill !== skillFilter) {skillFilter = skill} else {skillFilter = null}} } on:keypress={() => skillFilter = skill}>
                        {skill}
                        {#if skillFilter === skill}
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 ml-2 mr-0">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        {/if}
                    </div>
                    <span>x {count}</span>
                </div>
            {/each}
        </div>
        <div class="lg:columns-3 p-2 py-2 pt-8 h-auto container grid lg:grid-cols-3 gap-4">
            {#each Object.entries(resumes) as [pubkey, r]}
                {#if (skillFilter === null) || (r.resume.hasSkill(skillFilter))}
                    <div class="card rounded-box max-w-full xl:w-full gap-4 px-4 mx-3 xl:mx-0 py-6 mb-3 flex-shrink-0 place-items-center items-center shadow-xl bg-slate-400/70 text-primary-content h-full">
                        <div class="avatar mask mask-squircle h-40 w-40">
                            <img src={(pubkey in metadata ? metadata[pubkey].picture : null) ?? profilePicturePlaceHolder} alt="" />
                        </div>
                        <div>
                            <div class="w-full text-center">
                                <div class="text-lg text-black font-extrabold">{pubkey in metadata ? metadata[pubkey].name : encodeNpub(pubkey).substring(0, 10) + "..."}</div>
                                <div class="text-sm text-black my-3 ">{r.resume.jobTitle}</div>
                            </div>
                            <div class="w-full mt-2 text-center text-black">
                                {#each r.resume.skills as skill}
                                    <div class="badge badge-primary badge-outline mr-2 mb-1">{skill.skill}</div>
                                {/each}
                            </div>
                            <div class="w-full mt-2 text-center text-black">
                                <p>{@html r.resume.bio.substring(0,150)}{#if r.resume.bio.length > 150}...{/if}</p>
                            </div>
                        </div>
                        <div>
                            <button class="btn btn-primary btn-sm mr-2"
                                    on:click={() => onView(r.resume, pubkey in metadata ? metadata[pubkey].name : null, pubkey in metadata ? metadata[pubkey].picture : null)}>
                                View
                            </button>
                            <a class="btn btn-primary btn-sm" href="https://snort.social/p/{encodeNpub(pubkey)}" target="_blank" rel="noreferrer">
                                Contact
                            </a>
                        </div>
                    </div>
                {/if}
            {/each}
            {#each Object.entries(resumes) as [pubkey, r]}
                {#if (skillFilter === null) || (r.resume.hasSkill(skillFilter))}
                    <div class="card rounded-box max-w-full xl:w-full gap-4 px-4 mx-3 xl:mx-0 py-6 mb-3 flex-shrink-0 place-items-center items-center shadow-xl bg-slate-400/70 text-primary-content h-full">
                        <div class="avatar mask mask-squircle h-40 w-40">
                            <img src={(pubkey in metadata ? metadata[pubkey].picture : null) ?? profilePicturePlaceHolder} alt="" />
                        </div>
                        <div>
                            <div class="w-full text-center">
                                <div class="text-lg text-black font-extrabold">{pubkey in metadata ? metadata[pubkey].name : encodeNpub(pubkey).substring(0, 10) + "..."}</div>
                                <div class="text-sm text-black my-3 ">{r.resume.jobTitle}</div>
                            </div>
                            <div class="w-full mt-2 text-center text-black">
                                {#each r.resume.skills as skill}
                                    <div class="badge badge-primary badge-outline mr-2 mb-1">{skill.skill}</div>
                                {/each}
                            </div>
                            <div class="w-full mt-2 text-center text-black">
                                <p>{@html r.resume.bio.substring(0,150)}{#if r.resume.bio.length > 150}...{/if}</p>
                            </div>
                        </div>
                        <div>
                            <button class="btn btn-primary btn-sm mr-2"
                                    on:click={() => onView(r.resume, pubkey in metadata ? metadata[pubkey].name : null, pubkey in metadata ? metadata[pubkey].picture : null)}>
                                View
                            </button>
                            <a class="btn btn-primary btn-sm" href="https://snort.social/p/{encodeNpub(pubkey)}" target="_blank" rel="noreferrer">
                                Contact
                            </a>
                        </div>
                    </div>
                {/if}
            {/each}
            {#each Object.entries(resumes) as [pubkey, r]}
                {#if (skillFilter === null) || (r.resume.hasSkill(skillFilter))}
                    <div class="card rounded-box max-w-full xl:w-full gap-4 px-4 mx-3 xl:mx-0 py-6 mb-3 flex-shrink-0 place-items-center items-center shadow-xl bg-slate-400/70 text-primary-content h-full">
                        <div class="avatar mask mask-squircle h-40 w-40">
                            <img src={(pubkey in metadata ? metadata[pubkey].picture : null) ?? profilePicturePlaceHolder} alt="" />
                        </div>
                        <div>
                            <div class="w-full text-center">
                                <div class="text-lg text-black font-extrabold">{pubkey in metadata ? metadata[pubkey].name : encodeNpub(pubkey).substring(0, 10) + "..."}</div>
                                <div class="text-sm text-black my-3 ">{r.resume.jobTitle}</div>
                            </div>
                            <div class="w-full mt-2 text-center text-black">
                                {#each r.resume.skills as skill}
                                    <div class="badge badge-primary badge-outline mr-2 mb-1">{skill.skill}</div>
                                {/each}
                            </div>
                            <div class="w-full mt-2 text-center text-black">
                                <p>{@html r.resume.bio.substring(0,150)}{#if r.resume.bio.length > 150}...{/if}</p>
                            </div>
                        </div>
                        <div>
                            <button class="btn btn-primary btn-sm mr-2"
                                    on:click={() => onView(r.resume, pubkey in metadata ? metadata[pubkey].name : null, pubkey in metadata ? metadata[pubkey].picture : null)}>
                                View
                            </button>
                            <a class="btn btn-primary btn-sm" href="https://snort.social/p/{encodeNpub(pubkey)}" target="_blank" rel="noreferrer">
                                Contact
                            </a>
                        </div>
                    </div>
                {/if}
            {/each}
        </div>
    {/if}
</div>
