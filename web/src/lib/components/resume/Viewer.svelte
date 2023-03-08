<script lang="ts">
    import type { UserResume } from "$lib/types/user";

    export let resume: UserResume;
    export let onViewFinished = () => {};
</script>

<div class="flex justify-center items-center mt-4 h-15 gap-8">
    <button class="btn btn-primary btn-lg" on:click|preventDefault={onViewFinished}>Back</button>
</div>

<div class="text-center mt-8 text-3xl">
    {resume.jobTitle}
</div>

<div class="flex flex-row gap-2 items-center justify-center">
    {#each resume.skills as skill}
        <div class="badge badge-primary badge-lg mt-4">{skill.skill}</div>
    {/each}
</div>

<p class="text-center text-xl mt-4">{resume.bio}</p>

{#if resume.desiredYearlySalaryUsd}
    <p class="text-center text-xl mt-4">
        Desired yearly salary (USD equivalent): {resume.desiredYearlySalaryUsd}
    </p>
{/if}

{#if resume.hourlyRateUsd}
    <p class="text-center text-xl mt-4">
        Hourly rate (USD equivalent): {resume.hourlyRateUsd}
    </p>
{/if}

{#if resume.bitcoinerQuestion}
    <p class="text-center text-lg mt-4">
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
            {education.education} {#if education.year}({education.year}){/if}
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
            <p>
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
            {achievement.achievement} {#if achievement.year}({achievement.year}){/if}
        {/each}
    </div>
{/if}