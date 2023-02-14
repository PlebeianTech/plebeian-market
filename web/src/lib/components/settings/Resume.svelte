<script lang="ts">
    import { onMount } from 'svelte';
    import { ErrorHandler, getResume, putResume } from "$lib/services/api";
    import { Info, token, user } from "$lib/stores";
    import { page } from '$app/stores';
    import { UserResumeAchievement, type UserResume } from "$lib/types/user";
    import MarkdownEditor from "$lib/components/MarkdownEditor.svelte";

    export let onSave: () => void = () => {};

    let resume: UserResume;

    let newAchievement = new UserResumeAchievement();

    $: saveButtonActive = $user && !saving;

    function addAchievement() {
        resume.achievements = [...resume.achievements, newAchievement];
        newAchievement = new UserResumeAchievement();
    }

    function removeAchievement(i) {
        resume.achievements = resume.achievements.slice(0, i).concat(resume.achievements.slice(i + 1));
    }

    let saving = false;
    async function save() {
        saving = true;

        putResume($token, resume,
            () => {
                Info.set("Your résumé has been saved!");
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
            getResume($token, (r) => resume = r);
        }
    });
</script>

{#if $page.url.pathname === "/settings"}
    <div class="text-2xl breadcrumbs">
        <ul>
            <li>Settings</li>
            <li>Résumé</li>
        </ul>
    </div>
{:else}
    <h2 class="text-2xl">Résumé</h2>
{/if}

<div class="flex justify-center items-center mt-4 h-15">
    {#if saveButtonActive}
        <button id="save-profile" class="btn btn-primary" on:click|preventDefault={save}>Save</button>
    {:else}
        <button class="btn" disabled>Save</button>
    {/if}
</div>

{#if resume}

<div class="w-full flex items-center justify-center mt-8">
    <div class="w-full">
        <div class="form-control w-full max-w-full">
            <label class="label" for="title">
                <span class="label-text">Job title</span>
            </label>
            <input bind:value={resume.jobTitle} type="text" name="title" class="input input-bordered" />
        </div>
        <MarkdownEditor mainTabName="Bio" showEditorButtons={false} bind:value={resume.bio} />
<!--
        <div>
            <div>
                {#each skills as skill}
                    <div class="badge badge-primary badge-lg mt-4">{skill}</div>
                    <button class="btn btn-circle btn-xs btn-error" on:click={() => removeSkill(skill)}>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                    <br />
                {/each}
                <div class="flex justify-center items-center mt-4">
                    <input type="text" bind:value={newSkill} placeholder="add a skill" class="input input-bordered input-primary w-full max-w-xs" on:keypress={skillKeyPress} />
                    <button class="btn btn-circle btn-xs btn-success ml-2" on:click={addSkill}>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12,0 V24 M0,12 H24" /></svg>
                    </button>
                </div>
            </div>
        </div>
-->
    </div>
</div>

<div class="divider my-8"></div>

<h3 class="text-2xl">Past achievements</h3>

<div class="overflow-x-auto w-full p-2">
    <table class="w-full">
        <tbody class="w-full whitespace-nowrap">
            {#each resume.achievements as achievement, i}
                <tr>
                    <td class="w-full">
                        {achievement.achievement}
                    </td>
                    <td>
                        {#if achievement.year}
                            {achievement.year}
                        {/if}
                    </td>
                    <td>
                        <button class="btn btn-circle btn-xs btn-error" on:click={() => removeAchievement(i)}>
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                        </button>
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>

<div class="flex justify-center items-center mt-4">
    <div class="flex flex-col">
        <div class="w-full">
            <label class="label" for="title">
                <span class="label-text">Achievement</span>
            </label>
            <input bind:value={newAchievement.achievement} type="text" name="achievement" class="input input-bordered w-full" />
        </div>
        <div class="flex flex-row">
            <div class="w-1/2 max-w-xs">
                <label class="label" for="year">
                    <span class="label-text">year</span>
                </label>
                <input bind:value={newAchievement.year} type="number" name="year" class="input input-bordered w-full max-w-xs" />
            </div>
        </div>
    </div>
    <div class="w-4">
        {#if newAchievement.validate()}
            <button class="btn btn-circle btn-xs btn-success ml-2" on:click={addAchievement}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12,0 V24 M0,12 H24" /></svg>
            </button>
        {:else}
            <button class="btn btn-disabled btn-xs ml-2" disabled>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12,0 V24 M0,12 H24" /></svg>
            </button>
        {/if}
    </div>
</div>

<div class="divider my-8"></div>

<MarkdownEditor mainTabName="Why do you want to be paid in bitcoin?" showEditorButtons={false} bind:value={resume.bitcoinerQuestion} />

{/if}