export const site = {
  name: 'Vasile Grafu',
  title: 'Engineering Manager | Solutions Architect | Software Architecture, Cloud & Agentic AI',
  // The line under the name in the banner, on every page. Deliberately not
  // the job title: `title` above still carries that, on the Career and Skills
  // pages and in the resume.
  strapline: 'Pursuing ideas',
  // Short form. Feeds the meta/OG description and the resume PDF, where length
  // is constrained — keep it near 160 characters.
  //
  // Getters rather than strings: the year count is derived, and vite.config.ts
  // imports this module before Vite has substituted `__BUILD_YEAR__`. Nothing
  // there reads either of these, so they are only evaluated inside the app.
  get tagline() {
    return `Engineer and architect with ${yearsSince(careerStart)}+ years in software — from game programming to cloud platforms handling millions of requests a day, now building agentic AI systems.`;
  },
  // Long form, the summary at the top of the resume PDF — free to say more
  // than the meta description can.
  get intro() {
    return `${yearsSince(careerStart)}+ years in software development, and every phase of it: shaping the specification, designing the architecture, writing the code, holding the quality, shipping the release, and running it in production. Usually several of those at once.`;
  },
  location: 'Bucharest, Romania',
  email: 'vasilegrafu@gmail.com',
  phone: '+40 722 635 785',
  linkedin: 'https://www.linkedin.com/in/vasile-grafu-6a99369',
  github: 'https://github.com/vasilegrafu',
  url: 'https://vasilegrafu.github.io',
};

/**
 * The years every tenure figure counts from: January 2005 at Ubisoft, and
 * January 2017, the Team Manager role at Consignor — the first time the job was
 * running people rather than leading the work. The Career and home tiles count
 * from these, so the two pages cannot drift apart or go stale.
 */
export const careerStart = 2005;
export const leadershipStart = 2017;

/**
 * The AWS services in use today. The nShift role and the Skills list are the
 * same stack by definition — Skills is what I use now — so they share one
 * string and cannot drift apart. The earlier roles carry their own, smaller
 * lists: the stack grew over the years and the entries should show that.
 *
 * Services only, never sub-resources: no load balancers, no target groups.
 */
export const awsStack = 'AWS (EC2, ECS, Fargate, RDS, S3, CloudFormation, CDK)';

/** Substituted at build time by `define` in vite.config.ts. */
declare const __BUILD_YEAR__: number;

/**
 * Whole years since `year`, taken from the build year rather than the clock at
 * render time — the prerendered HTML and the page hydrating it have to agree
 * (docs/SEO.md). A function on purpose: vite.config.ts imports this module for
 * `site`, and `__BUILD_YEAR__` only exists once Vite has substituted it.
 */
export const yearsSince = (year: number) => __BUILD_YEAR__ - year;

export interface Role {
  company: string;
  position: string;
  period: string;
  location: string;
  /** What the company is. Career page only — the PDF uses `aboutShort`. */
  about?: string;
  /** One line of company context for the resume, where `about` is too long. */
  aboutShort?: string;
  /** What I did there. Optional — some roles are carried by their bullets alone. */
  summary?: string;
  /** Ordered most resume-worthy first — the PDF may show only the first few. */
  bullets: string[];
  /**
   * How many leading bullets describe the scope of the role (the teams I ran)
   * rather than the work itself. The Career page gives those stronger emphasis.
   */
  leadBullets?: number;
  /**
   * How many bullets the resume PDF shows for this role. Omit to show all.
   * Lets the Career page carry full detail while the PDF stays at two pages.
   */
  pdfBullets?: number;
  /**
   * Lucide icon for this role, used on the Career timeline and the profile
   * page's Background list. Lives on the role rather than in a positional
   * array beside it, so inserting a role cannot shift every icon below it.
   */
  icon: string;
  /**
   * Technologies in a fixed order — language and framework, data, frontend,
   * AI, cloud, delivery — then at most one practice chip last (Prince2,
   * AI-assisted engineering). Technologies only: activities and products
   * belong in the bullets. Commas inside a chip; the slash in `C# / .NET`
   * is part of the name, not a separator.
   */
  tech?: string[];
}

export const experience: Role[] = [
  {
    company: 'nShift (formerly Consignor)',
    position: 'Engineering Manager',
    icon: 'lucide:sparkles', // nShift — AI era
    period: 'January 2022 – Present',
    location: 'Bucharest, Romania',
    aboutShort:
      'Global delivery-management platform — over 1,000 carriers across some 190 countries.',
    about:
      'nShift is a global leader in delivery and experience management software, formed in 2021 from the merger of Consignor, Unifaun and Transsmart. Its cloud platform covers the whole parcel journey — checkout delivery options, rule-based carrier selection, label and document generation, tracking, and returns — connecting retailers, 3PLs and manufacturers to a network of over 1,000 carriers across some 190 countries, with integrations into 450+ OMS, ERP and WMS systems.',
    summary:
      'I lead the Webservices Team — one of the company’s core teams — building applications that handle millions of requests per day and support multiple business-critical systems. Most weeks I wear several hats at once: software architect, software engineer, AI engineer and engineering manager. In practice that means owning the architecture, writing a large share of the code, building the AI systems on top of it, and still setting direction for the team.',
    bullets: [
      'Software architecture: design and implementation of scalable, secure, and maintainable systems.',
      'Software engineering: shared components, application structure, data flow, database design, security, and infrastructure.',
      'AI engineering: the agentic systems built on top — LLMs, agent orchestration, RAG, and MCP servers and tool integrations.',
      'Solution Architect: cloud environments on AWS, and the CI/CD pipelines that deliver to them.',
      'Test automation: helped build the end-to-end test framework covering the APIs and the UI, and the tests that run on it.',
      'Lead and manage the Webservices Team: setting clear goals, providing direction, and keeping every member motivated and effective.',
      'Establish engineering processes and standards: consistent development practices that improve collaboration, maintain quality, and accelerate delivery.',
      'Provide technical guidance: solving complex issues alongside developers, reviewing designs, and making critical decisions on challenging topics.',
      'Recruit and develop engineers: active role in hiring, onboarding, and mentoring to build a skilled, cohesive team.',
      'Act as Scrum Master: stand-ups, planning, retrospectives, and effective communication between Product Owners and developers.',
    ],
    tech: [
      'C# / .NET, ASP.NET Core',
      'Python, FastAPI, SQLAlchemy',
      'SQL Server, PostgreSQL',
      'JavaScript, TypeScript, ReactJS, Material UI',
      'LLMs, Agents, RAG, MCP',
      awsStack,
      'Git, GitHub, GitHub Actions',
      'Docker',
      'pytest, Playwright',
      'AI-assisted engineering',
    ],
  },
  {
    company: 'Consignor (formerly Edisoft)',
    position: 'Team Manager',
    icon: 'lucide:globe', // two teams, e-commerce reach
    period: 'January 2017 – January 2022',
    location: 'Bucharest, Romania',
    aboutShort:
      'Scandinavia’s leading multi-carrier shipping software; 10,000+ business customers.',
    about:
      'Founded in Oslo in 1997, Consignor grew into one of the largest suppliers of transport administration and multi-carrier shipping software in Scandinavia, serving more than 10,000 business customers from offices in Norway, Sweden, Denmark, Finland, Romania and the UK. In 2021 it merged with Unifaun and Transsmart to become nShift.',
    summary:
      'I led two teams — the Webservices Team and the Integration Team — and wore the hat each situation demanded: Team Manager, Technical Lead, Project Manager (Prince2), or Software Developer. In practice that meant hiring and training the people who joined, owning the critical architecture decisions, running projects across team boundaries — and still writing code myself. These years also spanned the 2021 merger with Unifaun and Transsmart that turned Consignor into nShift.',
    bullets: [
      'Webservices Team: ran the web services serving the client components of the Consignor business.',
      'Integration Team: brought Consignor functionality to the major e-commerce and checkout platforms — WooCommerce, Magento and Klarna.',
      'Software architecture: the design decisions across the Consignor suite — service boundaries, shared components and the data model.',
      'Software engineering: shared components, application structure and database design across the suite, and the PHP integrations into the e-commerce platforms.',
      'Solution Architect: the AWS environments the platform ran on, from EC2 to Docker containers on ECS and Fargate, and the CI/CD pipelines that deployed to them.',
      'Team leadership: set goals and direction for both teams, keeping two groups with very different missions pulling toward one platform.',
      'Technical guidance: worked through the hard problems alongside the developers.',
      'Recruit and develop engineers: hiring, onboarding, and training the people who joined either team.',
    ],
    leadBullets: 2,
    tech: [
      'C# / .NET, ASP.NET Core',
      'PHP',
      'AWS (EC2, ECS, Fargate, S3, CloudFormation)',
      'Git, Bitbucket, GitLab',
      'Docker',
      'Project Management (Prince2)',
    ],
  },
  {
    company: 'Consignor (formerly Edisoft)',
    position: 'Technical Lead',
    icon: 'lucide:layers', // the platform applications
    period: '2010 – 2017',
    location: 'Bucharest, Romania',
    summary:
      'I led the Webservices Team, behind the 50 web services that served over 10,000 business clients in the Consignor application suite.',
    bullets: [
      'Applications at the core of the platform: built Routing Codes, Address Lookup and Sending Edifacts — all still part of the nShift ecosystem today.',
      'Custom Price Calculation Engine: kept developing the engine I had built the year before, as its use spread across the platform.',
      'Software architecture and solution design: owned the design decisions across the Consignor suite, from service boundaries to data model.',
      'Software engineering: wrote a large share of the code myself, alongside the team rather than above it.',
      'Mentoring: brought on junior and senior developers, and helped hire the people who joined.',
    ],
    leadBullets: 2,
    tech: [
      'C# / .NET, ASP.NET MVC, WCF',
      'SQL Server',
      'JavaScript, jQuery',
      'AWS (EC2, S3)',
      'SVN and Git (Bitbucket, GitLab)',
    ],
  },
  {
    company: 'Edisoft',
    position: 'Senior Software Engineer',
    icon: 'lucide:code-xml', // hands-on developer
    period: '2009 – 2010',
    location: 'Bucharest, Romania',
    aboutShort: 'Later rebranded as Consignor; today part of nShift.',
    about:
      'Edisoft was later rebranded as Consignor — the Scandinavian multi-carrier shipping software business that merged with Unifaun and Transsmart in 2021 to become nShift. The name changed; the platform and the team did not.',
    summary:
      'I designed and built the Custom Price Calculation Engine, and when the manager left the following year I took over the Webservices Team as Technical Lead.',
    bullets: [
      'Custom Price Calculation Engine: designed and built it — customers upload the rates they have agreed with their carriers, the engine parses that price sheet, and it calculates the price of each shipment from it.',
      'Still in production: written in 2009 and running today across nShift, where thousands of customers depend on it.',
      'Outgrew one developer: the application became large enough to need its own team, first at Edisoft and later Consignor, building price sheets with customers and training them on it.',
    ],
    tech: [
      'C# / .NET, ASP.NET Web Forms, WCF',
      'SQL Server',
      'SVN',
    ],
  },
  {
    company: 'TeamNet',
    position: 'Senior Software Engineer',
    icon: 'lucide:package', // TeamNet — ERP
    period: '2008 – 2009',
    location: 'Bucharest, Romania',
    aboutShort: 'Romanian technology and systems-integration company.',
    about:
      'TeamNet International, a Romanian technology and systems-integration company delivering software, IT infrastructure, and technology solutions for major public- and private-sector organizations.',
    summary:
      'I was responsible for Optimus ERP modules end to end, from specification through testing and deployment.',
    bullets: [
      'Optimus ERP modules: managed them through every development step, from specification to testing and deployment.',
      'Feature planning: built development plans for new features with the design department.',
      'Quality and maintenance: enhanced existing features, and triaged and resolved every defect raised by the Quality Department.',
    ],
    tech: ['C# / .NET, WinForms', 'SQL Server'],
  },
  {
    company: 'Ubisoft',
    position: 'Game Programmer',
    icon: 'lucide:gamepad-2', // Ubisoft
    period: 'January 2005 – June 2008',
    location: 'Bucharest, Romania',
    aboutShort: 'One of the world’s largest video game publishers.',
    about:
      'Ubisoft is a French video game publisher founded in 1986 by the Guillemot brothers and now one of the largest in the world, with studios across more than 45 locations behind franchises such as Assassin’s Creed, Far Cry, Rainbow Six and Prince of Persia. Ubisoft Bucharest, opened in 1992, was the company’s first production studio outside France and grew into one of its largest.',
    summary:
      'I designed, developed, and optimized gameplay and platform modules on four shipped and in-development titles.',
    bullets: [
      'Silent Hunter 4: designed and built the framework managing the evolution of the Crew, Weapons, and Equipment of the U-Boat simulator.',
      'King Kong (PC): Windows Media Center integration, multithreaded rendering, and the security module.',
      'Blazing Angels (PC): Save/Load system and Media Center shell implementation.',
      'Tom Clancy’s FireHawk: ERS (Enhanced Reality System) module.',
    ],
    tech: [
      'C++, STL',
      'Linear algebra, Calculus, Probability',
    ],
  },
];

export interface SkillCategory {
  group: string;
  icon: string; // lucide icon name, used on the Skills page (the PDF ignores it)
  blurb: string; // one-line intro, used on the Skills page (the PDF ignores it)
  items: string[];
}

export const skills: SkillCategory[] = [
  {
    group: 'AI & Machine Learning',
    icon: 'lucide:brain',
    blurb: 'Agentic systems in production — and the theory underneath them.',
    items: [
      'AI-Assisted Software Development',
      'Agentic Architectures & LLM Orchestration',
      'RAG (Retrieval-Augmented Generation)',
      'MCP Gateways, MCP Servers & tool integrations',
      'Machine Learning, Neural Networks & Deep Learning Foundations',
    ],
  },
  {
    group: 'Backend & Architecture',
    icon: 'lucide:server',
    blurb: 'Designing and building the services that carry the business.',
    items: [
      'C#, .NET, ASP.NET Core, Entity Framework, LINQ',
      'Python, FastAPI, Flask, SQLAlchemy',
      'Solution & Software Architecture',
      'Framework Design',
      'API Design (REST, SOAP/WCF)',
    ],
  },
  {
    group: 'Cloud, Data & DevOps',
    icon: 'lucide:cloud',
    blurb: 'Running systems reliably on AWS, from database to pipeline.',
    items: [
      awsStack,
      'Git, GitHub, GitHub Actions',
      'Docker, CI/CD',
      'End-to-end testing (pytest, Playwright)',
      'SQL Server, PostgreSQL',
      'Database Design, Relational Databases',
    ],
  },
  {
    group: 'Leadership & Management',
    icon: 'lucide:users',
    blurb: 'Building, growing, and running engineering teams.',
    items: [
      'Engineering Management',
      'Team & Technical Leadership',
      'Hiring & Mentoring',
      'Agile / Scrum',
      'Project Management (Prince2)',
      'Strategic Planning',
    ],
  },
  {
    group: 'Frontend & Web',
    icon: 'lucide:monitor',
    blurb: 'Interfaces for the platforms and tools I build.',
    items: [
      'JavaScript, TypeScript, jQuery',
      'ReactJS, Material UI',
      'HTML, CSS, SASS',
      'Astro, Tailwind CSS, HTMX',
      'Server-Rendered Web (ASP.NET MVC + Razor, Flask + Jinja)',
    ],
  },
  {
    group: 'Foundations',
    icon: 'lucide:sigma',
    blurb: 'The math and fundamentals everything else stands on.',
    items: [
      'Probability, Linear Algebra, Calculus, Statistics',
      'Data Structures & Algorithms',
      'Problem Solving & Analytical Thinking',
      'Software Architecture Principles',
      'Design Patterns & Clean Code',
    ],
  },
];

export const education = [
  {
    school: 'Academy of Economic Studies, Bucharest',
    degree: 'Master of Science in Computer Science, Specialization in Project Management',
    period: '2000 – 2002',
  },
  {
    school: 'Academy of Economic Studies, Bucharest',
    degree:
      'Bachelor in Business Administration, Major in Computer Science, Specialization in Computer Science Applied in Business',
    period: '1995 – 2000',
  },
];

export interface Project {
  title: string;
  /** Lucide icon, on the project rather than in a positional array. */
  icon: string;
  role: string;
  /** What the system is, in a sentence or two. My part goes in `did`. */
  description: string;
  /**
   * What I did on it, four to six lines. `label` is the bold lead a skimming
   * reader takes in; `text` is the detail for a technical one.
   */
  did?: { label: string; text: string }[];
  tags: string[];
}

// The systems I built at nShift, for the Projects page only: written for
// recruiters and employers, so what each one does and my part in it, not how.
// The order is deliberate — the AI work first. Neither the printable resume
// nor the Career page reads this list.
//
// Public page: no internal names, hostnames, suppliers, customers, scopes or
// costs. Backends are named by business function only.
export const projects: Project[] = [
  {
    title: 'nShift Companion',
    icon: 'lucide:bot-message-square',
    role: 'Lead engineer · nShift · 2025 – present',
    description:
      'A production AI assistant built into nShift’s checkout, tracking, returns and portal products. Each product has its own agent, with its own knowledge and tools, and the agents can consult one another.',
    did: [
      {
        label: 'Multi-agent design',
        text: 'designed how a question reaches the right agent — straight to the product’s own agent when the product is known, so follow-up questions keep their context — and let agents consult one another, with a guard against delegating in circles.',
      },
      {
        label: 'Five production agents',
        text: 'built and shipped one agent per product area, each with its own prompts, tools and knowledge, and admin-managed starter questions.',
      },
      {
        label: 'Knowledge pipeline (RAG)',
        text: 'imports the help-centre articles, keeps them in sync on a schedule, limits each agent to its own product’s content, and cites the source articles in its answers.',
      },
      {
        label: 'Actions, not just answers',
        text: 'connected the agents to company systems through MCP, and built a support-ticket flow where the assistant drafts the ticket and the user confirms it before anything is created.',
      },
    ],
    tags: [
      'Python',
      'FastAPI',
      'AWS Bedrock',
      'Claude',
      'Multi-agent',
      'RAG',
      'MCP',
      'React',
      'AWS ECS Fargate',
      'Docker',
      'GitHub Actions',
    ],
  },
  {
    title: 'Enterprise MCP Gateway',
    icon: 'lucide:workflow',
    role: 'Creator and project owner · nShift · 2026 – present',
    description:
      'One secure, governed entry point between AI agents and the company’s systems, built on the Model Context Protocol (MCP). AI clients — the company’s own assistant and third-party agent platforms — connect to the gateway, which checks who they are and what they may use, and routes each request to the right tool server: tracking, user management, invoicing and more.',
    did: [
      {
        label: 'From idea to production',
        text: 'owned the initiative and led the technical approach on the open-source agentgateway, taking it from the first commit to production in four environments.',
      },
      {
        label: 'Security model',
        text: 'every caller’s identity is checked, permissions are enforced per tool server, and private backends receive only the identity details they need.',
      },
      {
        label: 'Two gateways, one catalogue each',
        text: 'an internal and an external variant, each publishing only the tools its audience may use, with one endpoint per product that combines several tool servers and shows each caller only what they are allowed.',
      },
      {
        label: 'Existing APIs as AI tools',
        text: 'published existing REST APIs as MCP tools without rewriting them, and built a sample tool server as a template for other teams.',
      },
      {
        label: 'Shipped like a product',
        text: 'versioned, immutable releases with rollback, health checks and security scanning, and integration tests that check every deployed environment in one run.',
      },
      {
        label: 'Adoption',
        text: 'wrote the architecture docs and the onboarding guide teams use to add their own tool servers, and connected the company’s AI assistant to the first tools.',
      },
    ],
    tags: ['MCP', 'Python', 'AWS ECS Fargate', 'Docker', 'GitHub Actions'],
  },
  {
    title: 'Custom Price Calculation',
    icon: 'lucide:calculator',
    role: 'Lead developer · nShift · 2026 – present',
    description:
      'Where nShift’s customers keep the prices they have negotiated with carriers — zones, weight bands, surcharges, discounts — as digital rate cards they edit themselves. The engine then answers one question exactly: what does this shipment cost under this customer’s agreement? It replaces the custom-price part of an older pricing service.',
    did: [
      {
        label: 'Engine and API',
        text: 'designed the new pricing API as its own web service and built most of its endpoints and the logic behind the rate-card editor, as main developer on a three-person team.',
      },
      {
        label: 'Engine roadmap',
        text: 'own the new engine features rate managers need to model real carrier agreements: several price sheets per service, a richer pricing model, ready-made templates, and drafts, versions and publishing.',
      },
      {
        label: 'Mistakes caught before they cost money',
        text: 'every change goes through one checked intake, so a rate card cannot go live half-valid, and every error points to the exact line so rate managers can fix it themselves.',
      },
      {
        label: 'Customer migration',
        text: 'own the move of existing customers’ rate cards from the legacy service, kept backwards compatible and locked in by regression tests, so migrated customers see exactly the same prices.',
      },
      {
        label: 'AI in rate management',
        text: 'built a proof of concept where an AI agent edits a rate card from a plain-language instruction — “raise the fuel surcharge to 15%” — and returns a validated sheet with a summary of the changes.',
      },
      {
        label: 'Quality built in',
        text: 'automated API tests on every environment, browser tests for the editor, and the user manual and design documentation.',
      },
    ],
    tags: [
      'C#',
      '.NET 10',
      'React',
      'TypeScript',
      'SQL Server',
      'Claude Agent SDK',
      'AWS ECS Fargate',
      'Docker',
      'GitHub Actions',
    ],
  },
  {
    title: 'Address Intelligence Service',
    icon: 'lucide:map-pin',
    role: 'Creator and technical lead · nShift · 2023 – present',
    description:
      'nShift’s shared service for understanding addresses across many countries: autocomplete as you type, address and postcode validation, geocoding and distance. It powers the pickup-point search shoppers see at checkout, where an exact location decides which parcel lockers and service points they are offered.',
    did: [
      {
        label: 'From proof of concept to platform',
        text: 'designed and built the service from the first commit and grew it into a production platform other teams rely on; technical owner for three years, writing most of the code and guiding the developers and QA engineers who joined.',
      },
      {
        label: 'Seven address features in one API',
        text: 'autocomplete, geocoding, reverse geocoding, postcode validation, postcode details, address splitting and distance.',
      },
      {
        label: 'Fast as you type',
        text: 'in-memory search indexes so suggestions come back without a database round-trip, plus work on startup time, memory and behaviour under traffic spikes, proven with stress tests before rollout.',
      },
      {
        label: 'Quality without the cost',
        text: 'answers come from a licensed address dataset first, with a paid map service only as a fallback, and the data refreshes itself on a schedule.',
      },
    ],
    tags: ['C#', '.NET', 'ASP.NET Core', 'SQL Server', 'AWS ECS Fargate', 'Docker', 'GitHub Actions'],
  },
  {
    title: 'FileWatcher',
    icon: 'lucide:cloud',
    role: 'Technical lead · nShift · 2026 – present',
    description:
      'Many shipping customers still run warehouse, ERP and label systems that exchange files through folders. FileWatcher is a small agent installed on the customer’s own machine — Windows, Linux or macOS — that watches local folders and remote FTP, FTPS and SFTP servers and delivers every finished file to nShift reliably, even through network drops, restarts and updates.',
    did: [
      {
        label: 'Technical lead',
        text: 'own the project and steer the developers on it, including an external contractor, from requirements to release.',
      },
      {
        label: 'Management web app',
        text: 'built most of the local web app installers and support use every day: accounts, profiles, delivery endpoints, watch targets, settings, audit events and the status of every file.',
      },
      {
        label: 'Reliable delivery',
        text: 'worked on the core pipeline — spotting new files, waiting until a file is completely written, uploading and archiving — and added a deduplication key so a repeated delivery is safely ignored.',
      },
    ],
    tags: ['C#', '.NET 10', 'ASP.NET Core', 'SFTP', 'GitHub Actions'],
  },
];
