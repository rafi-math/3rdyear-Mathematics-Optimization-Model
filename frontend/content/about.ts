/**
 * Author-editable facts and biography for section 05 (Author details).
 * Keep strictly to verified facts from the case study report.
 */

export interface AuthorFacts {
  name: string;
  department: string;
  university: string;
  location: string;
  session: string;
  reportTitle: string;
  reportDate: string;
  githubRepo: string;
  githubProfile: string;
  email: string;
  event?: string;
  bioParagraphs: string[];
}

export const authorFacts: AuthorFacts = {
  name: "Md. Ali Arman Rafi",
  department: "Department of Mathematics",
  university: "University of Chittagong",
  location: "Chittagong, Bangladesh",
  session: "2021-22 session (did not participate in the survey to preserve neutrality)",
  reportTitle: "Optimising a Scarce Study Budget: A Linear Programming Approach to Undergraduate Academic Workload",
  reportDate: "18 September 2026",
  githubRepo: "https://github.com/rafi-math/3rdyear-Mathematics-Optimization-Model",
  githubProfile: "https://github.com/rafi-math",
  email: "sbrafi10@gmail.com",
  event: "",
  bioParagraphs: [
    "I am a student in the Department of Mathematics at the University of Chittagong. This tool grew out of a case study report I wrote on how a third-year student might split a limited weekly study budget across ten courses.",
    "The budget came from a survey of 147 classmates across the 2021-22 and 2022-23 cohorts. The linear programme was initially formulated and solved in Python using PuLP and CBC.",
    "The code, survey data, and model formulations are public on GitHub, allowing anyone to verify the arithmetic or test their own difficulty ratings.",
  ],
};
