<script lang="ts">
    import { onMount } from 'svelte';
    import { SimplePool } from 'nostr-tools';
    import { getPreferredPublicKey } from "$lib/nostr/utils";
    import { subscribeResume, publishResume } from "$lib/services/nostr";
    import { Info, Error } from "$lib/stores";
    import { UserResume, UserResumeAchievement, UserResumeEducation, UserResumeExperience, UserResumePortfolio, UserResumeSkill } from "$lib/types/user";
    import { getMonthName } from "$lib/utils";
    import MonthPicker from "$lib/components/MonthPicker.svelte";
    import YearPicker from "$lib/components/YearPicker.svelte";
    import Plus from "$lib/components/icons/Plus.svelte";
    import X from "$lib/components/icons/X.svelte";
    import Loading from "$lib/components/Loading.svelte";

    export let onEditFinished: () => void = () => {};

    let pool = new SimplePool();

    let resume: UserResume = new UserResume();

    // timestamp of the Nostr event, so we can always pick the last version
    // NB: initially set to 0, so we pick whatever is in Nostr, if there is anything!
    let resumeCreatedAt = 0;
    let timeoutPublishResume = 20000;
    let resumeNotPublishedTimer = null;

    let newSkill = new UserResumeSkill();
    let newPortfolio = new UserResumePortfolio();
    let newEducation: UserResumeEducation | null = null;
    let newExperience: UserResumeExperience | null = null;
    let newAchievement: UserResumeAchievement | null = null;

    let availableForWork = false;

    $: saveButtonActive = !saving;

    function addSkill() {
        if (newSkill.validate()) {
            resume.skills = [...resume.skills, newSkill];
            newSkill = new UserResumeSkill();
        }
    }

    function removeSkill(i) {
        resume.skills = resume.skills.slice(0, i).concat(resume.skills.slice(i + 1));
    }

    function addPortfolio() {
        if (newPortfolio.validate()) {
            resume.portfolio = [...resume.portfolio, newPortfolio];
            newPortfolio = new UserResumePortfolio();
        }
    }

    function removePortfolio(i) {
        resume.portfolio = resume.portfolio.slice(0, i).concat(resume.portfolio.slice(i + 1));
    }

    function addEducation() {
        if (newEducation && newEducation.validate()) {
            resume.education = [...resume.education, newEducation];
            newEducation = new UserResumeEducation();
        }
    }

    function removeEducation(i) {
        resume.education = resume.education.slice(0, i).concat(resume.education.slice(i + 1));
    }

    function addExperience() {
        if (newExperience && newExperience.validate()) {
            resume.experience = [...resume.experience, newExperience];
            newExperience = new UserResumeExperience();
        }
    }

    function removeExperience(i) {
        resume.experience = resume.experience.slice(0, i).concat(resume.experience.slice(i + 1));
    }

    function addAchievement() {
        if (newAchievement && newAchievement.validate()) {
            resume.achievements = [...resume.achievements, newAchievement];
            newAchievement = new UserResumeAchievement();
        }
    }

    function removeAchievement(i) {
        resume.achievements = resume.achievements.slice(0, i).concat(resume.achievements.slice(i + 1));
    }

    let saving = false;
    async function save() {
        let notified = false;
        saving = true;

        resumeNotPublishedTimer = setTimeout(
            () => {
                saving = false;
                Error.set("We couldn't publish your résumé");
            },
            timeoutPublishResume);

        await publishResume(pool, resume,
            () => {
                console.log(' --- publishResume');
                if (!notified) {
                    console.log(' --- publishResume !notified');
                    clearTimeout(resumeNotPublishedTimer);
                    notified = true;
                    saving = false;
                    Info.set("Your résumé has been saved!");
                    onEditFinished();
                }
            });
    }

    onMount(async () => {
        subscribeResume(pool, await getPreferredPublicKey(null),
            (r, rcAt) => {
                if (rcAt > resumeCreatedAt) {
                    resumeCreatedAt = rcAt;
                    resume = r;
                    availableForWork = resume.desiredYearlySalaryUsd !== null || resume.hourlyRateUsd !== null;
                }
            });
    });
</script>

{#if !window.nostr}
    <div class="alert alert-error shadow-lg">
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span>Please use a browser with a Nostr extension (such as Alby)!</span>
        </div>
    </div>
{:else}
    <div class="flex justify-center items-center mt-4 h-15 gap-8">
        {#if saveButtonActive}
            <button class="btn btn-primary btn-lg" on:click|preventDefault={save}>Save</button>
        {:else}
            <button class="btn" disabled>Save</button>
        {/if}
        <button class="btn btn-secondary btn-lg" on:click|preventDefault={onEditFinished}>Cancel</button>
    </div>

    <div class="w-full flex items-center justify-center mt-8">
        <div class="w-full">
            <div class="form-control w-full max-w-full">
                <label class="label" for="title">
                    <span class="label-text">Job title</span>
                </label>
                <input bind:value={resume.jobTitle} type="text" name="title" class="input input-bordered" />
            </div>

            <div class="form-control w-full max-w-full pt-4">
                <label class="label" for="bio">
                    <span class="label-text">Bio</span>
                </label>
                <textarea bind:value={resume.bio} name="bio" rows="6" class="textarea textarea-bordered h-48"></textarea>
            </div>

            <div class="divider my-8"></div>

            <h3 class="text-2xl">Skills</h3>

            <div>
                <div>
                    {#each resume.skills as skill, i}
                        <div class="badge badge-primary badge-lg mt-4">{skill.skill}</div>
                        <button class="btn btn-circle btn-xs btn-error" on:click={() => removeSkill(i)}><X /></button>
                        <br />
                    {/each}
                    <div class="flex justify-center items-center mt-4 gap-4">
                        <div class="flex flex-col">
                            <input type="text" bind:value={newSkill.skill} placeholder="add a skill" class="input input-bordered input-primary w-full max-w-xs" on:keypress={(e) => { if (e.key === "Enter") addSkill(); }} />
                        </div>
                        <div>
                            {#if newSkill.validate()}
                                <button class="btn btn-s btn-circle btn-ghost ml-2" on:click={addSkill}><Plus /></button>
                            {:else}
                                <button class="btn btn-s btn-circle btn-disabled ml-2" disabled><Plus /></button>
                            {/if}
                        </div>
                    </div>
                </div>
            </div>

            <div class="divider my-8"></div>

            <h3 class="text-2xl">Portfolio</h3>

            <div>
                <div>
                    {#each resume.portfolio as portfolio, i}
                        <a class="link mt-4" href={portfolio.url}>{portfolio.url}</a>
                        <button class="btn btn-circle btn-xs btn-error" on:click={() => removePortfolio(i)}><X /></button>
                        <br />
                    {/each}
                    <div class="flex justify-center items-center mt-4 gap-4">
                        <div class="flex flex-col">
                            <input type="text" bind:value={newPortfolio.url} placeholder="https://" class="input input-bordered input-primary w-full max-w-xs" on:keypress={(e) => { if (e.key === "Enter") addPortfolio(); }} />
                        </div>
                        <div>
                            {#if newPortfolio.validate()}
                                <button class="btn btn-s btn-circle btn-ghost ml-2" on:click={addPortfolio}><Plus /></button>
                            {:else}
                                <button class="btn btn-s btn-circle btn-disabled ml-2" disabled><Plus /></button>
                            {/if}
                        </div>
                    </div>
                </div>
            </div>

            <div class="divider my-8"></div>

            <div class="flex justify-center items-center gap-4">
                <h3 class="text-2xl mb-0">Education</h3>
                <button class="btn btn-circle btn-s btn-ghost" on:click={() => newEducation = new UserResumeEducation()}><Plus /></button>
            </div>

            <div class="overflow-x-auto w-full p-2">
                <ul class="w-full">
                    {#each resume.education as education, i}
                        <li class="p-3 rounded-md bg-base-300 mt-2">
                            <div class="flex justify-center items-center gap-2 md:gap-4">
                                <span class="flex-auto">
                                    {education.education}
                                </span>
                                <span class="flex-none">
                                    {#if education.year}
                                        {education.year}
                                    {/if}
                                </span>
                                <span class="flex-none">
                                    <button class="btn btn-circle btn-xs btn-error" on:click={() => removeEducation(i)}><X /></button>
                                </span>
                            </div>
                        </li>
                    {/each}
                </ul>
            </div>

            {#if newEducation}
                <div class="flex justify-center items-center mt-4 gap-4">
                    <div class="flex flex-col">
                        <div class="w-full">
                            <label class="label" for="education">
                                <span class="label-text">Education</span>
                            </label>
                            <input bind:value={newEducation.education} type="text" name="education" class="input input-bordered w-full" on:keypress={(e) => { if (e.key === "Enter") addEducation(); }} />
                        </div>
                        <div class="flex flex-row">
                            <div class="w-1/2 max-w-xs">
                                <label class="label" for="year">
                                    <span class="label-text">year</span>
                                </label>
                                <YearPicker bind:value={newEducation.year} />
                            </div>
                        </div>
                    </div>
                    <div>
                        {#if newEducation.validate()}
                            <button class="btn btn-s btn-circle btn-ghost" on:click={addEducation}><Plus /></button>
                        {:else}
                            <button class="btn btn-s btn-circle btn-disabled" disabled><Plus /></button>
                        {/if}
                    </div>
                    <div>
                        <button class="btn btn-xs btn-circle btn-error" on:click={() => newEducation = null}><X /></button>
                    </div>
                </div>
            {/if}

            <div class="divider my-8"></div>

            <div class="flex justify-center items-center gap-4">
                <h3 class="text-2xl mb-0">Experience</h3>
                <button class="btn btn-circle btn-s btn-ghost" on:click={() => newExperience = new UserResumeExperience()}><Plus /></button>
            </div>

            <div class="overflow-x-auto w-full p-2">
                <ul class="w-full">
                        {#each resume.experience as experience, i}
                            <li class="p-3 rounded-md bg-base-300 mt-2">
                                <div class="flex justify-center items-center gap-2 md:gap-4">
                                    <div class="flex-auto">
                                        <span class="text-lg">
                                            <em>{experience.jobTitle}</em>
                                        </span>
                                        <br />
                                        <span class="text-lg">
                                            <strong>{experience.organization}</strong>
                                        </span>
                                    </div>
                                    <span class="flex-auto">
                                        {#if experience.fromYear}
                                            {experience.fromYear}
                                            {#if experience.fromMonth}
                                                ({getMonthName(experience.fromMonth)})
                                            {/if}
                                            &mdash;
                                        {/if}
                                        {#if experience.toYear}
                                            {experience.toYear}
                                            {#if experience.toMonth}
                                                ({getMonthName(experience.toMonth)})
                                            {/if}
                                        {/if}
                                    </span>
                                    <span class="flex-none">
                                        <button class="btn btn-circle btn-xs btn-error" on:click={() => removeExperience(i)}><X /></button>
                                    </span>
                                </div>
                                <p class="mt-2">
                                    {experience.description}
                                </p>
                            </li>
                        {/each}
                </ul>
            </div>

            {#if newExperience}
                <div class="flex justify-center items-center mt-4 gap-4">
                    <div class="flex flex-col">
                        <div class="w-full">
                            <label class="label" for="experienceJobTitle">
                                <span class="label-text">Job title</span>
                            </label>
                            <input bind:value={newExperience.jobTitle} type="text" name="experienceJobTitle" class="input input-bordered w-full" on:keypress={(e) => { if (e.key === "Enter") addExperience(); }} />
                        </div>
                        <div class="w-full">
                            <label class="label" for="experienceOrganization">
                                <span class="label-text">Organization</span>
                            </label>
                            <input bind:value={newExperience.organization} type="text" name="experienceOrganization" class="input input-bordered w-full" on:keypress={(e) => { if (e.key === "Enter") addExperience(); }} />
                        </div>
                        <div class="form-control w-full max-w-full pt-4">
                            <label class="label" for="experienceDescription">
                                <span class="label-text">Description</span>
                            </label>
                            <textarea bind:value={newExperience.description} name="experienceDescription" rows="6" class="textarea textarea-bordered h-48"></textarea>
                        </div>
                        <div class="flex flex-row">
                            <div class="w-1/2 max-w-xs">
                                <label class="label" for="experienceFromYear">
                                    <span class="label-text">from year</span>
                                </label>
                                <YearPicker bind:value={newExperience.fromYear} />
                            </div>
                            <div class="w-1/2 max-w-xs pl-4">
                                <label class="label" for="experienceFromMonth">
                                    <span class="label-text">month</span>
                                </label>
                                <MonthPicker bind:value={newExperience.fromMonth} />
                            </div>
                        </div>
                        <div class="flex flex-row">
                            <div class="w-1/2 max-w-xs">
                                <label class="label" for="experienceToYear">
                                    <span class="label-text">to year</span>
                                </label>
                                <YearPicker bind:value={newExperience.toYear} />
                            </div>
                            <div class="w-1/2 max-w-xs pl-4">
                                <label class="label" for="experienceToMonth">
                                    <span class="label-text">month</span>
                                </label>
                                <MonthPicker bind:value={newExperience.toMonth} />
                            </div>
                        </div>
                    </div>
                    <div>
                        {#if newExperience.validate()}
                            <button class="btn btn-s btn-circle btn-ghost ml-2" on:click={addExperience}><Plus /></button>
                        {:else}
                            <button class="btn btn-s btn-disabled ml-2" disabled><Plus /></button>
                        {/if}
                    </div>
                    <div>
                        <button class="btn btn-xs btn-circle btn-error" on:click={() => newExperience = null}><X /></button>
                    </div>
                </div>
            {/if}

            <div class="divider my-8"></div>

            <div class="flex justify-center items-center gap-4">
                <h3 class="text-2xl mb-0">Achievements</h3>
                <button class="btn btn-circle btn-s btn-ghost" on:click={() => newAchievement = new UserResumeAchievement()}><Plus /></button>
            </div>

            <div class="overflow-x-auto w-full p-2">
                <ul class="w-full">
                    {#each resume.achievements as achievement, i}
                        <li class="p-3 rounded-md bg-base-300 mt-2">
                            <div class="flex justify-center items-center gap-2 md:gap-4">
                                <span class="flex-auto">
                                    {achievement.achievement}
                                </span>
                                <span class="flex-none">
                                    {#if achievement.year}
                                        {achievement.year}
                                    {/if}
                                </span>
                                <span class="flex-none">
                                    <button class="btn btn-circle btn-xs btn-error" on:click={() => removeAchievement(i)}><X /></button>
                                </span>
                            </div>
                        </li>
                    {/each}
                </ul>
            </div>

            {#if newAchievement}
                <div class="flex justify-center items-center mt-4 gap-4">
                    <div class="flex flex-col">
                        <div class="w-full">
                            <label class="label" for="achievement">
                                <span class="label-text">Achievement</span>
                            </label>
                            <input bind:value={newAchievement.achievement} type="text" name="achievement" class="input input-bordered w-full" on:keypress={(e) => { if (e.key === "Enter") addAchievement(); }} />
                        </div>
                        <div class="flex flex-row">
                            <div class="w-1/2 max-w-xs">
                                <label class="label" for="year">
                                    <span class="label-text">year</span>
                                </label>
                                <YearPicker bind:value={newAchievement.year} />
                            </div>
                        </div>
                    </div>
                    <div>
                        {#if newAchievement.validate()}
                            <button class="btn btn-s btn-circle btn-ghost ml-2" on:click={addAchievement}><Plus /></button>
                        {:else}
                            <button class="btn btn-s btn-disabled ml-2" disabled><Plus /></button>
                        {/if}
                    </div>
                    <div>
                        <button class="btn btn-xs btn-circle btn-error" on:click={() => newAchievement = null}><X /></button>
                    </div>
                </div>
            {/if}

            <div class="divider my-8"></div>

            <div class="form-control w-full max-w-full pt-4">
                <label class="label" for="bitcoinerQuestion">
                    <span class="label-text">Why do you want to be paid in bitcoin?</span>
                </label>
                <textarea bind:value={resume.bitcoinerQuestion} name="bitcoinerQuestion" rows="6" class="textarea textarea-bordered h-48"></textarea>
            </div>

            <div class="divider my-8"></div>

            <div class="mx-4 md:flex md:justify-center md:items-center md:gap-4">
                <h3 class="text-2xl">Are you available for work?</h3>
                <input type="checkbox" name="availableForWork" class="toggle toggle-lg" bind:checked={availableForWork} on:change={() => {if (!availableForWork) { resume.desiredYearlySalaryUsd = null; resume.hourlyRateUsd = null; } }} />
            </div>

            {#if availableForWork}
                <div class="flex flex-col md:flex-row justify-center items-center">
                    <div>
                        <label class="label" for="desiredYearlySalaryUsd">
                            <span class="label-text">Desired yearly salary (USD equivalent)</span>
                        </label>
                        <input bind:value={resume.desiredYearlySalaryUsd} type="number" name="desiredYearlySalaryUsd" class="input input-bordered" />
                    </div>
                    <div class="ml-4">
                        <label class="label" for="hourlyRateUsd">
                            <span class="label-text">Hourly rate (USD equivalent)</span>
                        </label>
                        <input bind:value={resume.hourlyRateUsd} type="number" name="hourlyRateUsd" class="input input-bordered" />
                    </div>
                </div>
            {/if}
        </div>
    </div>

    <div class="flex justify-center items-center mt-10 h-15 gap-8">
        {#if saveButtonActive}
            <button class="btn btn-primary btn-lg" on:click|preventDefault={save}>Save</button>
        {:else}
            <button class="btn" disabled>Save</button>
        {/if}
        <button class="btn btn-secondary btn-lg" on:click|preventDefault={onEditFinished}>Cancel</button>
    </div>

    {#if saving}
        <Loading />
    {/if}
{/if}
