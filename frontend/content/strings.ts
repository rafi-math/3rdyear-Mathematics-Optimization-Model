/**
 * User-facing copy for Study budget.
 * Strictly adheres to 05_COPY_AND_VOICE_GUIDE.md.
 * No inline strings should be written directly in components.
 */

export const strings = {
  // 00 Masthead
  masthead: {
    siteName: "Study budget",
    navLinks: [
      { id: "calculator", label: "Calculator", href: "#calculator" },
      { id: "method", label: "Method", href: "#method" },
      { id: "case-study", label: "Case study", href: "#case-study" },
      { id: "about", label: "About", href: "#about" },
      { id: "source", label: "Source", href: "https://github.com/rafi-math/3rdyear-Mathematics-Optimization-Model" },
    ],
    units: {
      min: "MIN",
      h: "H",
    },
  },

  // 01 Intro
  intro: {
    statement: "Split your study hours across your courses and see the arithmetic.",
    body: "Enter your courses, their credits, how hard you find each one, and the hours you actually have. The tool solves a linear programme and shows how much time each course gets under three different rules.",
    limitLine: "It does not predict grades. It measures how well a plan fits the priorities you gave it.",
    flowSteps: [
      "1  Enter courses and hours",
      "2  Add your own rules",
      "3  Compare the three models",
    ],
    links: {
      goToCalculator: "Go to calculator ↓",
      loadCaseStudy: "Load the case study",
    },
  },

  // 02 Calculator - General
  calculator: {
    sectionNumber: "02",
    sectionTitle: "Calculator",
    caseStudyBanner: "You are looking at the case study.",
    clearCaseStudy: "Clear and start your own",
    runButton: "Run models",
    outOfDateNotice: "You have changed the plan since the last run.",
    loadingNotice: "Working",
    solverAsleepNotice: "The solver is starting up. This can take up to a minute.",
    offlineNotice: "You are offline. Your plan is saved in this browser.",
  },

  // Stage A: Plan
  stageA: {
    stepNumber: "A",
    title: "Plan",
    subtitle: "Input your courses, credit weightings, subjective difficulty, and available study hours.",
    parserLabel: "Paste, upload or speak your courses and hours.",
    parserHelp: "Text, a screenshot, a PDF or Word file, or a voice note. Nothing is filled in until you have checked it.",
    parserButtons: {
      readThis: "Read this",
      record: "Record",
      stop: "Stop",
    },
    tableHeaders: {
      course: "COURSE",
      credits: "CREDITS",
      difficulty: "DIFFICULTY",
      min: "MIN",
      max: "MAX",
      lock: "LOCK",
      actions: "",
    },
    difficultyLabels: {
      most_difficult: { label: "Most difficult", coeff: "1.2" },
      difficult: { label: "Difficult", coeff: "1.1" },
      medium: { label: "Medium", coeff: "1.0" },
      easy: { label: "Easy", coeff: "0.9" },
      easiest: { label: "Easiest", coeff: "0.8" },
    },
    difficultyHelp: "Your own rating. It is a judgement, not a measurement.",
    unassignedCheckbox: "Treat unassigned courses as Easiest (0.8), as the paper does.",
    unassignedWarning: "Difficulty rating is missing. Select a rating to proceed.",
    advancedToggle: "Advanced coefficient settings",
    budgetTitle: "Time available",
    budgetModes: {
      weekly: "Weekly",
      daily: "Daily",
      custom: "Custom periods",
    },
    daysPerWeekLabel: "Days per week",
    addCourseButton: "Add course",
    clearButton: "Clear",
    emptyState: "No courses yet. Add one, or load the case study.",
    pasteHint: "You can paste tab-separated rows directly from a spreadsheet.",
    courseCountWarning: "More than 30 courses entered. The solver will work normally, but the list is long.",
  },

  // Stage B: Rules
  stageB: {
    stepNumber: "B",
    title: "Rules",
    subtitle: "Add limits that apply to you. Each rule can be switched off without deleting it.",
    addRuleButton: "Add rule",
    ruleTypes: {
      min: "Course minimum",
      max: "Course maximum",
      lock: "Fixed block",
      boost: "Priority boost",
      dependency: "Course dependency",
      group_limit: "Group limit",
      unavailable: "Unavailable in period",
    },
    emptyState: "No custom rules added yet.",
  },

  // Stage C: Results
  stageC: {
    stepNumber: "C",
    title: "Results",
    subtitle: "Calculated study allocations across the three linear optimisation formulations.",
    roundingNote: "Rounded to the minute. The exact total is {total}.",
    tableHeaders: {
      course: "COURSE",
      modelA: "A · CREDITS",
      modelB: "B · CREDITS × DIFFICULTY",
      modelC: "C · DIMINISHING RETURNS",
      status: "STATUS",
    },
    modelCTag: "Added for this tool. It is not part of the paper.",
    whyDifferTitle: "Why the models differ",
    constraintsTitle: "What limited the answer",
    constraints: {
      budgetUsed: "The whole budget is used.",
      atMinimum: "At the minimum: {courses}.",
      atCap: "At the cap: {courses}.",
      unallocated: "Left unallocated: {time}.",
    },
    shadowPriceTitle: "Value of one more hour",
    shadowPriceBody: "One more hour, spent where it counts most, adds {value} to the objective. That is a score inside this model. It is not marks or CGPA. The next hour would go to {courses}.",
    checkLine: "Check: re-solving with 30 more minutes changes the objective by {delta}, which is {per_hour} per hour.",
    exportButtons: {
      csv: "Download CSV",
      pdf: "Download PDF",
      ics: "Add to calendar (.ics)",
    },
  },

  // 03 Method
  method: {
    sectionNumber: "03",
    sectionTitle: "Method",
    paragraphs: [
      "The two main models come from my paper. Model A weights each course by its credits. Model B weights it by credits times a difficulty coefficient from five levels, 1.2 down to 0.8. Both maximise the weighted study time, within the same limits.",
      "Each course gets at least 20 minutes by default. No course may take more than 1.3 times its proportional share of the budget. Courses with equal weights get equal time, otherwise the solver could choose between them arbitrarily.",
      "Model C is not in the paper. I added it because the fifth hour on one subject usually helps less than the first hour on another. The falling values are assumptions I chose, and you can change them.",
      "The shadow price says how much the objective would rise if the budget grew by one hour. It belongs to the model's own score. It says nothing direct about exam results.",
    ],
  },

  // 04 Case study
  caseStudy: {
    sectionNumber: "04",
    rowLabel: "Case study · Third-year Mathematics, University of Chittagong",
    paragraph: "I surveyed third-year Mathematics students from the 2021-22 and 2022-23 sessions. 147 of the 200 eligible students replied, a response rate of 73.5%. From their answers I estimated a weekly self-study budget of 7.6 hours, which works out at under 46 minutes per course across ten courses.",
    tableNote: "As printed in the paper. Rounded to the minute, these columns add up to 7 h 40 m and 7 h 34 m. The exact values add up to 7 h 36 m.",
    limits: "The budget comes from one survey of one group of students. The difficulty ratings came from my own experience and from talking to classmates, so they are not a measured scale. The model is calibrated to this curriculum.",
    loadButton: "Load case study into calculator",
  },

  // 05 About
  about: {
    sectionNumber: "05",
    sectionTitle: "About",
    label: "ABOUT",
    factsHeading: "RESEARCH DETAILS",
  },

  // 06 Footer
  footer: {
    sectionNumber: "06",
    sectionTitle: "Colophon",
    dataNote: "Files you upload are read once to fill in the form and are not stored. Your plan stays in this browser.",
    links: {
      source: "Source code",
      paper: "Paper",
      contact: "Contact",
    },
  },

  // Errors and empty states
  errors: {
    parseFailed: "Could not read that. Paste the text instead, or enter the courses by hand.",
    parsePartial: "Some fields were missing. They are marked below.",
    parseBusy: "The reading service is busy. Try again in a minute, or type the plan in.",
    fileTooLarge: "That file is over {limit} MB.",
    fileType: "This tool reads text, images, PDF, Word and audio files.",
    infeasibleTemplate: "These rules cannot all hold. {reason} Relax one of them and run again.",
  },
};
