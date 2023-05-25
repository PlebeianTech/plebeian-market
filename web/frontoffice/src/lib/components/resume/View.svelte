<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { SimplePool } from 'nostr-tools';
    import { page } from "$app/stores";
    import type { UserResume } from "$lib/types/user";
    import Loading from "$lib/components/Loading.svelte";
    import Back from "$sharedLib/components/icons/Back.svelte";
    import Editor from "$lib/components/resume/Editor.svelte";
    import { encodeNpub } from "$lib/nostr/utils";
    import { subscribeResume, subscribeMetadata, closePool } from "$lib/services/nostr";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";

    export let pubkey: string;

    let edit = false;

    let userPubKey;

    let pool = new SimplePool();

    let resume: UserResume | null = null;
    let resumeCreatedAt: number = 0;

    let metadataSubscribed = false;
    let name: string;
    let picture: string;

    function loadResume() {
        subscribeResume(pubkey,
                (r, rcAt) => {
                    if (resumeCreatedAt < rcAt) {
                        resume = r;
                        resumeCreatedAt = rcAt;
                        if (!metadataSubscribed) {
                            metadataSubscribed = true;
                            subscribeMetadata([pubkey],
                                (_pk, m) => {
                                    if (m.name !== undefined) {
                                        name = m.name;
                                    }
                                    if (m.picture !== undefined) {
                                        picture = m.picture;
                                    }
                                });
                        }
                    }
            });
    }

    onMount(
        async () => {
            document.body.scrollTop = document.documentElement.scrollTop = 0;

            let parts = $page.url.href.split("#");
            if (parts.length === 2 && parts[1] === "edit") {
                edit = true;
            }

            loadResume();

            userPubKey = await (window as any).nostr.getPublicKey();
        }
    );
</script>

<div class="mx-auto w-full">
    {#if !edit}
        <div class="flex items-center mt-4 h-15 gap-8">
            <a class="btn btn-primary btn-outline" href="/skills">
                <Back />
                Back to the Skills market
            </a>
        </div>
    {/if}

    {#if resume === null}
        <Loading />
    {:else if edit}
        <Editor {pubkey} {resume} onEditFinished={() => { resume = null; edit = false; loadResume(); }} />
    {:else}
        <div class="flex justify-center items-center mt-8 h-15 gap-8">
            {#if resume && pubkey === userPubKey}
                <button class="btn btn-primary btn-lg" on:click|preventDefault={() => edit = true}>Edit</button>
            {/if}
            {#if pubkey}
                <a class="btn btn-primary btn-lg" href="https://snort.social/p/{encodeNpub(pubkey)}" target="_blank" rel="noreferrer">
                    Contact
                </a>
            {/if}
        </div>
        <div class="card bg-base-300 shadow-xl mt-4 pt-6 place-items-center items-center">
            <figure class="avatar mask mask-squircle h-80 w-80">
                <img src={picture ?? profilePicturePlaceHolder} alt="" />
            </figure>
            <div class="card-body w-full px-3">
                <h2 class="text-3xl text-center">{name}</h2>

                <div class="text-center mt-2 text-3xl">
                    {resume.jobTitle}
                </div>

                <div class="flex flex-wrap items-center justify-center w-full mt-2 text-center gap-2">
                    {#each resume.skills as skill}
                        <div class="badge badge-outline badge-primary badge-lg">{skill.skill}</div>
                    {/each}
                </div>

                <p class="text-center text-xl mt-4 whitespace-pre-wrap">{resume.bio}</p>

                {#if resume.desiredYearlySalaryUsd}
                    <p class="text-center text-xl mt-4">
                        Desired yearly salary (USD equivalent): {resume.desiredYearlySalaryUsd}
                    </p>
                {/if}

                {#if resume.hourlyRateUsd}
                    <p class="text-center text-xl mt-4 whitespace-pre-wrap">
                        Hourly rate (USD equivalent): {resume.hourlyRateUsd}
                    </p>
                {/if}

                {#if resume.bitcoinerQuestion}
                    <p class="text-center text-lg mt-4 whitespace-pre-wrap">
                        Why I want to be paid in bitcoin: {resume.bitcoinerQuestion}
                    </p>
                {/if}

                {#if resume.portfolio.length}
                    <div class="divider my-8"></div>

                    <h2 class="text-center text-3xl">Portfolio</h2>
                    <div class="text-center">
                        <ul>
                            {#each resume.portfolio as portfolio}
                            <li><a class="link" href={portfolio.url}>{portfolio.url}</a></li>
                            {/each}
                        </ul>
                    </div>
                {/if}

                {#if resume.education.length}
                    <div class="divider my-8"></div>

                    <h2 class="text-center text-3xl">Education</h2>
                    <div class="text-center text-xl">
                        {#each resume.education as education}
                            <p class="whitespace-pre-wrap">
                            {education.education} {#if education.year}({education.year}){/if}
                            </p>
                        {/each}
                    </div>
                {/if}

                {#if resume.experience.length}
                    <div class="divider my-8"></div>

                    <h2 class="text-center text-3xl">Experience</h2>
                    <div class="text-center text-xl">
                        {#each resume.experience as experience}
                            {experience.jobTitle} @ {experience.organization}
                            {#if experience.fromYear}
                                {experience.fromYear}
                                {#if experience.fromMonth}
                                    ({experience.fromMonth})
                                {/if}
                                &mdash;
                            {:else}
                                ?
                            {/if}
                            {#if experience.toYear}
                                {experience.toYear}
                                {#if experience.toMonth}
                                    ({experience.toMonth})
                                {/if}
                            {:else}
                                ?
                            {/if}
                            <p class="whitespace-pre-wrap">
                                {experience.description}
                            </p>
                        {/each}
                    </div>
                {/if}

                {#if resume.achievements.length}
                    <div class="divider my-8"></div>

                    <h2 class="text-center text-3xl">Achievements</h2>
                    <div class="text-center text-xl">
                        {#each resume.achievements as achievement}
                            <p class="whitespace-pre-wrap">
                            {achievement.achievement} {#if achievement.year}({achievement.year}){/if}
                            </p>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    {/if}

    {#if !edit}
        <div class="flex items-center mt-4 h-15 gap-8">
            <a class="btn btn-primary btn-outline" href="/skills">
                <Back />
                Back to the Skills market
            </a>
        </div>
    {/if}
</div>
