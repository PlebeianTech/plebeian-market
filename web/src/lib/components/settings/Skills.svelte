<script lang="ts">
    import { onMount } from 'svelte';
    import { ErrorHandler, putProfile, getEntities, postEntity, putEntity } from "$lib/services/api";
    import { Info, Error, token, user } from "$lib/stores";
    import { page } from '$app/stores';
    import { UserAchievement, userAchievementFromJson } from "$lib/types/user";
    import ListView, { ListViewStyle } from "$lib/components/ListView.svelte";
    import UserAchievementCard from "$lib/components/UserAchievementCard.svelte";
    import UserAchievementEditor from "$lib/components/UserAchievementEditor.svelte";

    export let onSave: () => void = () => {};

    let skills: string[] = [];
    let achievements: UserAchievement[] = [];

    let newSkill: string = "";

    $: addedSkills = skills.filter(s => !$user || $user.skills.indexOf(s) === -1);
    $: removedSkills = $user ? $user.skills.filter(s => skills.indexOf(s) === -1) : [];

    $: saveButtonActive = $user && !saving && (addedSkills.length !== 0 || removedSkills.length !== 0);

    function skillKeyPress(e) {
        if (e.key === "Enter") {
            if (newSkill.length > 21) {
                Error.set("Skill should be less than 21 characters long.");
                return;
            }
            skills = [...skills, newSkill]; // NB: push won't work, as Svelte won't detect the change to the array
            newSkill = "";
        }
    }

    function removeSkill(skill) {
        let i = skills.indexOf(skill);
        skills = skills.slice(0, i).concat(skills.slice(i + 1));
    }

    let saving = false;
    function save() {
        saving = true;
        putProfile($token, {skills},
            u => {
                user.set(u);
                Info.set("Your skills have been saved!");
                saving = false;
                onSave();
            },
            new ErrorHandler(true, () => saving = false));
    }

    onMount(async () => {
        if ($user) {
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
            <li>Skills & achievements</li>
        </ul>
    </div>
{:else}
    <h2 class="text-2xl">Skills & achievements</h2>
{/if}

<div class="w-full flex items-center justify-center mt-8">
    <div>
        {#if skills.length === 0}
            <div class="alert alert-info shadow-lg">
                <div>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span>List some of your skills below.</span>
                </div>
            </div>
        {/if}
        <div>
            {#each skills as skill}
                <div class="badge badge-primary badge-lg mt-4">{skill}</div>
                <button class="btn btn-circle btn-xs btn-error" on:click={() => removeSkill(skill)}>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
                <br />
            {/each}
            <input type="text" bind:value={newSkill} placeholder="add a skill" class="mt-4 input input-bordered input-primary w-full max-w-xs" on:keypress={skillKeyPress} />
        </div>
    </div>
</div>

<div class="flex justify-center items-center mt-4 h-15">
    {#if saveButtonActive}
        <button id="save-profile" class="btn btn-primary" on:click|preventDefault={save}>Save</button>
    {:else}
        <button class="btn" disabled>Save</button>
    {/if}
</div>

<div class="my-8"></div>

<ListView
    loader={{endpoint: "users/me/achievements", responseField: 'achievements', fromJson: userAchievementFromJson}}
    postEndpoint={"users/me/achievements"}
    editor={UserAchievementEditor}
    card={UserAchievementCard}
    style={ListViewStyle.List}>
    <div slot="new-entity" class="w-full grid place-items-center" let:setCurrent={setCurrent}>
        <button class="btn btn-secondary" on:click|preventDefault={() => setCurrent(new UserAchievement())}>Add achievement</button>
    </div>
</ListView>
