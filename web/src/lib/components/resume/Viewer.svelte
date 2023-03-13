<script lang="ts">
    import { onMount } from 'svelte';
    import type { UserResume } from "$lib/types/user";
    import profilePicturePlaceHolder from "$lib/images/profile_picture_placeholder.svg";

    export let resume: UserResume;
    export let name: string | null;
    export let picture: string | null;

    export let onViewFinished = () => {};

    onMount(
        () => {
            document.body.scrollTop = document.documentElement.scrollTop = 0;
        }
    );
</script>

<div class="flex items-center mt-4 h-15 gap-8">
    <button class="btn btn-primary btn-outline" on:click|preventDefault={onViewFinished}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 16.811c0 .864-.933 1.405-1.683.977l-7.108-4.062a1.125 1.125 0 010-1.953l7.108-4.062A1.125 1.125 0 0121 8.688v8.123zM11.25 16.811c0 .864-.933 1.405-1.683.977l-7.108-4.062a1.125 1.125 0 010-1.953L9.567 7.71a1.125 1.125 0 011.683.977v8.123z" />
        </svg>
        Back to the Skills market
    </button>
</div>

<div class="card bg-base-300 shadow-xl mt-4 pt-6 place-items-center items-center">
    <figure class="avatar mask mask-squircle h-80 w-80">
        <img src={picture ?? profilePicturePlaceHolder} alt="" />
    </figure>
    <div class="card-body">
        <h2 class="text-3xl text-center">{name}</h2>

        <div class="text-center mt-4 text-3xl">
            {resume.jobTitle}
        </div>

        <div class="flex flex-row gap-2 items-center justify-center">
            {#each resume.skills as skill}
                <div class="badge badge-outline badge-primary badge-lg mt-4">{skill.skill}</div>
            {/each}
        </div>

        <p class="text-center text-xl mt-4">{resume.bio}</p>

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

        {#if resume.portfolio.length !== 0}
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

        {#if resume.experience.length !== 0}
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

        {#if resume.achievements.length !== 0}
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

<div class="flex items-center mt-4 h-15 gap-8">
    <button class="btn btn-primary btn-outline" on:click|preventDefault={onViewFinished}>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 mr-2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 16.811c0 .864-.933 1.405-1.683.977l-7.108-4.062a1.125 1.125 0 010-1.953l7.108-4.062A1.125 1.125 0 0121 8.688v8.123zM11.25 16.811c0 .864-.933 1.405-1.683.977l-7.108-4.062a1.125 1.125 0 010-1.953L9.567 7.71a1.125 1.125 0 011.683.977v8.123z" />
        </svg>
        Back to the Skills market
    </button>
</div>
