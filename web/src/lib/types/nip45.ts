import type { IEntity } from "$lib/types/base";

export class NostrStall {
    jobTitle: string = "";
    bio: string = "";
    desiredYearlySalaryUsd: number | null = null;
    hourlyRateUsd: number | null = null;
    bitcoinerQuestion: string = "";
    skills: UserResumeSkill[] = [];
    portfolio: UserResumePortfolio[] = [];
    education: UserResumeEducation[] = [];
    experience: UserResumeExperience[] = [];
    achievements: UserResumeAchievement[] = [];
/*
    public validate() {
        return this.jobTitle !== "" && this.skills.length !== 0;
    }

    public toJson() {
        return {
            job_title: this.jobTitle,
            bio: this.bio,
            desired_yearly_salary_usd: this.desiredYearlySalaryUsd,
            hourly_rate_usd: this.hourlyRateUsd,
            bitcoiner_question: this.bitcoinerQuestion,
            skills: this.skills.map(s => s.toJson()),
            portfolio: this.portfolio.map(p => p.toJson()),
            education: this.education.map(e => e.toJson()),
            experience: this.experience.map(e => e.toJson()),
            achievements: this.achievements.map(a => a.toJson()),
        };
    }

    public static fromJson(json: any): UserResume {
        let r = new UserResume();
        r.jobTitle = <string>json.job_title;
        r.bio = <string>json.bio;
        r.desiredYearlySalaryUsd = <number | null>json.desired_yearly_salary_usd;
        r.hourlyRateUsd = <number | null>json.hourly_rate_usd;
        r.bitcoinerQuestion = <string>json.bitcoiner_question;
        r.skills = (<any[]>json.skills).map(s => UserResumeSkill.fromJson(s));
        r.portfolio = (<any[]>json.portfolio).map(p => UserResumePortfolio.fromJson(p));
        r.education = (<any[]>json.education)
            .sort((a, b) => {return a.year <= b.year ? 1 : -1})
            .map(e => UserResumeEducation.fromJson(e));
        r.experience = (<any[]>json.experience)
            .sort((a, b) => {if (b.to_year === null) {return 1}; return a.to_year <= b.to_year ? 1 : -1})
            .map(e => UserResumeExperience.fromJson(e));
        r.achievements = (<any[]>json.achievements)
            .sort((a, b) => {return a.year <= b.year ? 1 : -1})
            .map(a => UserResumeAchievement.fromJson(a));
        return r;
    }
*/
}

/*
export interface ShoppingCart {
    stall_id: string;
    stall: {};
    products: Map<string, ShoppingCartItem>;
}
*/
export interface ShoppingCartItem {
    id: string
    name: string;
    description: string;
    price: number;
    currency: string;
    image: string;
    quantity: number;
    orderQuantity: number;
    created_at: number;
    stall_id: string;
    merchantPubkey: string;
}
