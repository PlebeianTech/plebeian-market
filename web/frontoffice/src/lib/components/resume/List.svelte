<script lang="ts">
    import { onDestroy, onMount } from 'svelte';
    import { encodeNpub, newNostrConversation } from "$lib/nostr/utils";
    import type { UserResume } from "$lib/types/user";
    import { subscribeResumes, subscribeMetadata, type UserMetadata } from "$lib/services/nostr";
    import Loading from "$lib/components/Loading.svelte";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";

    const QUERY_BATCH_SIZE = 100;
    const CHECK_METADATA_DELAY = 1000;

    let checkMetadataTimer: ReturnType<typeof setTimeout> | null = null;

    let resumes: {[pubkey: string]: {resume: UserResume, createdAt: number}} = {};
    let metadataRequested: string[] = [];
    let metadata: {[pubkey: string]: UserMetadata} = {};

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
            subscribeMetadata(pubkeysToQuery,
                (pk, m) => {
                    if (!(pk in metadata)) {
                        metadata[pk] = m;
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
        subscribeResumes(
            (pk, r, rcAt) => {
                if (pk === "ec79b568bdea63ca6091f5b84b0c639c10a0919e175fa09a4de3154f82906f25") { // CM
                    return;
                }
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
    })
</script>

{#if Object.keys(resumes).length === 0}
    <Loading />
{:else}
    <div class="rounded-box flex flex-wrap items-center justify-center max-w-full xl:w-full h-full gap-3 px-4 mx-6 xl:mx-2 py-6 mb-3 place-items-center items-center shadow-xl bg-base-300 night:bg-slate-800 text-white-content night:text-primary-content">
        <div class="w-full items-center justify-center"><b>Filter</b> profiles with these tags:</div>
        {#each Object.entries(skills) as [skill, count]}
            <div class="float badge badge-primary badge-lg cursor-pointer" class:badge-outline={skill !== skillFilter}
                 on:click={() => {if (skill !== skillFilter) {skillFilter = skill} else {skillFilter = null}}}
                 on:keypress={() => {if (skill !== skillFilter) {skillFilter = skill} else {skillFilter = null}}}>
                <span>{skill}</span> <span class="ml-2">({count})</span>
                {#if skillFilter === skill}
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5 ml-2 -mr-1">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                {/if}
            </div>
        {/each}
    </div>
    <div class="lg:columns-3 p-2 py-2 pt-1 h-auto container grid lg:grid-cols-3 gap-4">
        {#each Object.entries(resumes) as [pubkey, r]}
            {#if (r.resume.jobTitle !== "" && r.resume.skills.length !== 0) && ((skillFilter === null) || (r.resume.hasSkill(skillFilter)))}
                <div class="card rounded-box max-w-full xl:w-full h-full gap-4 px-4 mx-3 xl:mx-0 pt-4 pb-1 mb-3 flex-shrink-0 place-items-center items-center shadow-xl bg-base-300 night:bg-slate-800 text-white-content night:text-primary-content">
                    <div class="avatar mask mask-squircle h-40 w-40">
                        <img src={(pubkey in metadata ? metadata[pubkey].picture : null) ?? profilePicturePlaceHolder} alt="" />
                    </div>
                    <div>
                        <div class="w-full text-center">
                            <div class="text-xl font-extrabold">{pubkey in metadata ? metadata[pubkey].name : encodeNpub(pubkey).substring(0, 10) + "..."}</div>
                            <div class="text-base my-3 ">{r.resume.jobTitle}</div>
                        </div>
                        <div class="w-full mt-2 text-center">
                            {#each r.resume.skills as skill}
                                <div class="badge badge-primary badge-outline mr-2 mb-1">{skill.skill}</div>
                            {/each}
                        </div>
                        <div class="w-full mt-2 text-center">
                            <p>{@html r.resume.bio.substring(0,150)}{#if r.resume.bio.length > 150}...{/if}</p>
                        </div>
                    </div>
                    <div>
                        <a class="btn btn-primary btn-sm mr-2" href="/p/{pubkey}">View</a>
                        <a class="btn btn-primary btn-sm" on:click={() => newNostrConversation(pubkey)}>Contact</a>
                    </div>
                </div>
            {/if}
        {/each}
    </div>
{/if}

