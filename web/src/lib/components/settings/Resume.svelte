<script lang="ts">
    import { onMount } from 'svelte';
    import { ErrorHandler, putProfile, getEntities, postEntityAsync, deleteEntityAsync } from "$lib/services/api";
    import { Info, Error as ErrorStore, token, user } from "$lib/stores";
    import { page } from '$app/stores';
    import { UserAchievement, userAchievementFromJson } from "$lib/types/user";
    import { getMonthName } from '$lib/utils';
    import MarkdownEditor from "$lib/components/MarkdownEditor.svelte";
    import type { HttpError } from '@sveltejs/kit/src/runtime/control';

    export let onSave: () => void = () => {};

    let jobTitle: string = "";
    let bio: string = "";
    let bitcoinerQuestion: string = "";

    let skills: string[] = [];
    let newSkill: string = "";
    $: addedSkills = skills.filter(s => !$user || $user.skills.indexOf(s) === -1);
    $: removedSkills = $user ? $user.skills.filter(s => skills.indexOf(s) === -1) : [];

    let achievements: UserAchievement[] = [];
    let newAchievement: UserAchievement = new UserAchievement();
    let addedAchievements: UserAchievement[] = [];
    let removedAchievements: UserAchievement[] = [];

    $: saveButtonActive = $user && !saving &&
        (jobTitle !== ($user.jobTitle || "")
        || bio !== ($user.bio || "")
        || bitcoinerQuestion !== ($user.bitcoinerQuestion || "")
        || addedSkills.length !== 0
        || removedSkills.length !== 0
        || addedAchievements.length !== 0
        || removedAchievements.length !== 0);

    function skillKeyPress(e) {
        if (e.key === "Enter") {
            addSkill();
        }
    }

    function addSkill() {
        if (newSkill.length === 0) {
            return;
        }
        if (newSkill.length > 21) {
                ErrorStore.set("Skill should be less than 21 characters long.");
                return;
        }
        skills = [...skills, newSkill]; // NB: push won't work, as Svelte won't detect the change to the array
        newSkill = "";
    }

    function removeSkill(skill) {
        let i = skills.indexOf(skill);
        skills = skills.slice(0, i).concat(skills.slice(i + 1));
    }

    function addAchievement() {
        achievements = [...achievements, newAchievement];
        addedAchievements = [...addedAchievements, newAchievement];
        newAchievement = new UserAchievement();
    }

    function removeAchievement(i) {
        let achievement = achievements[i];

        if (achievement.key === "") {
            // NB: if we want to remove an achievement that was just added (thus not sent to the API yet),
            // we should remove it from addedAchievements instead of adding it to removedAchievements :)
            for (let ii = 0; ii < addedAchievements.length; ii++) {
                let addedAchievement = addedAchievements[ii];
                if (addedAchievement.achievement === achievement.achievement) {
                    addedAchievements = addedAchievements.slice(0, ii).concat(addedAchievements.slice(ii + 1));
                    break;
                }
            }
        } else {
            removedAchievements = [...removedAchievements, achievements[i]];
        }
        achievements = achievements.slice(0, i).concat(achievements.slice(i + 1));
    }

    let saving = false;
    async function save() {
        saving = true;

        let promises: Promise<any>[] = [];
        for (const achievement of addedAchievements) {
            promises.push(postEntityAsync("users/me/achievements", $token, achievement));
        }
        for (const achievement of removedAchievements) {
            promises.push(deleteEntityAsync($token, achievement));
        }

        try {
            await Promise.all(promises).then(() => {
                putProfile($token, {jobTitle, bio, bitcoinerQuestion, skills},
                    u => {
                        user.set(u);
                        Info.set("Your résumé has been saved!");
                        addedAchievements = [];
                        removedAchievements = [];
                        getEntities({endpoint: "users/me/achievements", responseField: 'achievements', fromJson: userAchievementFromJson}, $token,
                            (entities) => {
                                achievements = <UserAchievement[]>entities;
                            }
                        );
                        saving = false;
                        onSave();
                    },
                    new ErrorHandler(true, () => saving = false));
            });
        } catch(error) {
            saving = false;
            if (error instanceof Error) {
                ErrorStore.set(error.message);
            }
        }
    }

    onMount(async () => {
        if ($user) {
            jobTitle = $user.jobTitle || "";
            bio = $user.bio || "";
            bitcoinerQuestion = $user.bitcoinerQuestion || "";
            skills = $user.skills;

            getEntities({endpoint: "users/me/achievements", responseField: 'achievements', fromJson: userAchievementFromJson}, $token,
                (entities) => {
                    achievements = <UserAchievement[]>entities;
                });
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

<div class="w-full flex items-center justify-center mt-8">
    <div class="w-full">
        <div class="form-control w-full max-w-full">
            <label class="label" for="title">
                <span class="label-text">Job title</span>
            </label>
            <input bind:value={jobTitle} type="text" name="title" class="input input-bordered" />
        </div>
        <MarkdownEditor mainTabName="Bio" showEditorButtons={false} bind:value={bio} />
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
    </div>
</div>

<div class="divider my-8"></div>

<h3 class="text-2xl">Past achievements</h3>

<div class="overflow-x-auto w-full p-2">
    <table class="w-full">
        <tbody class="w-full whitespace-nowrap">
            {#each achievements as achievement, i}
                <tr>
                    <td class="w-full">
                        {achievement.achievement}
                    </td>
                    <td>
                        {#if achievement.from_year || achievement.from_month}
                            from {achievement.from_year} {#if achievement.from_month}({getMonthName(achievement.from_month)}){/if}
                        {/if}
                        {#if achievement.to_year || achievement.to_month}
                            to {achievement.to_year} {#if achievement.to_month}({getMonthName(achievement.to_month)}){/if}
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
                <label class="label" for="from_year">
                    <span class="label-text">from year</span>
                </label>
                <input bind:value={newAchievement.from_year} type="number" name="from_year" class="input input-bordered w-full max-w-xs" />
            </div>
            <div class="w-1/2 max-w-xs ml-2">
                <label class="label" for="from_month">
                    <span class="label-text">month (number)</span>
                </label>
                <input bind:value={newAchievement.from_month} type="number" name="from_month" class="input input-bordered w-full max-w-xs" />
            </div>
            <div class="w-1/2 max-w-xs ml-2">
                <label class="label" for="to_year">
                    <span class="label-text">to year</span>
                </label>
                <input bind:value={newAchievement.to_year} type="number" name="to_year" class="input input-bordered w-full max-w-xs" />
            </div>
            <div class="w-1/2 max-w-xs ml-2">
                <label class="label" for="to_month">
                    <span class="label-text">month (number)</span>
                </label>
                <input bind:value={newAchievement.to_month} type="number" name="to_month" class="input input-bordered w-full max-w-xs" />
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

<MarkdownEditor mainTabName="Why do you want to be paid in bitcoin?" showEditorButtons={false} bind:value={bitcoinerQuestion} />
