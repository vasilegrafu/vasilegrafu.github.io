// The resume's own content: what /resume-print renders and public/cv.pdf is
// printed from. It is written for the PDF and deliberately not shared with
// the Career and Projects pages: a resume says each fact once and keeps the
// detail the website has room for out of it.
//
// Plain punctuation only: no em dashes and no curly quotes. Applicant-tracking
// systems read the PDF's text, and those characters came out broken there.
//
// A bullet's `lead` is set in bold before its text, punctuation included, so
// it can end in a colon, a comma or nothing. Links inside a text are written
// as [label](url).
import { careerStart, leadershipStart, site, yearsSince } from './profile';

export interface ResumeBullet {
  lead?: string;
  text: string;
}

export interface ResumeProject {
  name: string;
  /** What the project is and why it matters, after the name. */
  context: string;
  bullets: ResumeBullet[];
}

export interface ResumeRole {
  period: string;
  location: string;
  position: string;
  company: string;
  /** One line of company context. */
  about?: string;
  bullets: ResumeBullet[];
  /** Shown under a "Key projects" label after the role's own bullets. */
  projects?: ResumeProject[];
  tech: string;
}

/** The year logistics software started: Edisoft, which became Consignor and nShift. */
const logisticsStart = 2009;

export const resume = {
  /** The site's own title, so the resume and the Career page cannot drift apart. */
  headline: site.title,

  // Functions rather than strings: the year counts come from the build year,
  // which only exists once Vite has substituted it (see yearsSince).
  summary: () => [
    `Engineering manager and hands-on architect with ${yearsSince(careerStart)}+ years in software, from game engines at Ubisoft to agentic AI platforms at nShift. I lead nShift's Webservices Team, whose services handle millions of requests a day for 10,000+ business clients. I am responsible for a multi-agent assistant inside nShift's products, central to its strategy for opening its products to customers through conversation, and the company's gateway that connects AI agents to its systems. ${yearsSince(leadershipStart)} years leading teams, five of them running two at once, and still writing a large share of the code.`,
  ],
  industry: () =>
    `logistics and delivery software (${yearsSince(logisticsStart)} years), video games (3 years)`,
  languages: 'Romanian (native), English (professional working proficiency)',

  skills: [
    {
      label: 'Agentic AI',
      text: 'multi-agent systems, RAG, MCP servers and gateways, LLMs (Claude, AWS Bedrock), AI-assisted engineering',
    },
    {
      label: 'Software and solution architecture',
      text: 'distributed services and APIs at scale, Domain-Driven Design, System Design; C#, .NET, ASP.NET Core, Entity Framework, Python, FastAPI',
    },
    {
      label: 'Cloud and DevOps',
      text: 'AWS (EC2, ECS, Fargate, RDS, S3, CloudFormation, CDK), Docker, GitHub Actions, CI/CD pipelines',
    },
    {
      label: 'Delivery and quality',
      text: 'from proof of concept to production, roadmaps, cross-team adoption; end-to-end and regression test automation (pytest, Playwright)',
    },
    {
      label: 'Data and frontend',
      text: 'SQL Server, PostgreSQL, database design, TypeScript, React',
    },
    {
      label: 'Engineering management',
      text: 'leading teams, hiring and mentoring, engineering standards, Agile and Scrum, Project Management (Prince2)',
    },
  ],

  openSource: {
    /** Opens the section, before the projects: why the research exists. Its
     *  last line leads straight into the two projects under it. */
    intro: {
      paragraphs: [
        'What occupies me most these days is how AI changes the way software gets built.',
        'AI makes code fast and cheap to write; it does not keep a system coherent, understood and under control. That is the part I care about: bringing AI into real engineering without losing what makes software trustworthy.',
        'Two things I am building toward it:',
      ],
    },
    /** The projects, in the order of the list above. Each one's `meta` is
     *  followed by its `links`, the repository first. */
    projects: [
      {
        meta: 'Developer tools, AI',
        year: '2026',
        links: [
          {
            label: 'github.com/vasilegrafu/project.specs-builder',
            href: 'https://github.com/vasilegrafu/project.specs-builder',
          },
          {
            label: 'Research article',
            href: 'https://vasilegrafu.github.io/research/specifications-as-a-graph',
          },
          {
            label: 'Video tutorials',
            href: 'https://www.youtube.com/playlist?list=PLAlCi-PFDpyk',
          },
        ],
        title: 'Specifications as a graph',
        where: 'personal project',
        bullets: [
          {
            text: 'A Claude Code skill that writes a product specification with you, in plain words, and keeps it as a graph of small, linked facts, so nothing is written twice and every change shows what it touches before it is made.',
          },
          {
            text: 'Reverse-engineers existing products with specialised agents; people read the result in a browser, coding agents query the same files. Published with a research article and a five-episode video tutorial series.',
          },
        ] as ResumeBullet[],
        tech: 'Claude Code, Agent Skills, multi-agent, Python, SQLite, JavaScript',
      },
      {
        meta: 'Developer tools, AI',
        year: '2026',
        links: [
          {
            label: 'github.com/vasilegrafu/project.application-builder',
            href: 'https://github.com/vasilegrafu/project.application-builder',
          },
        ],
        title: 'Controlling vibe coding',
        where: 'personal project (in progress)',
        bullets: [
          {
            text: 'A Claude Code skill that builds from existing codebases instead of from imagination: it measures what a codebase\'s parts agree on, writes new code to that contract, and asks wherever they disagree, so the AI decides only what you want it to decide.',
          },
          {
            text: 'Adds features in the house style, or migrates and translates whole applications to another stack, proven to behave like the original: it builds, its tests pass, and it runs the same as the original. Works at any codebase size, and reads Python, TypeScript, JavaScript and C#.',
          },
        ] as ResumeBullet[],
        tech: 'Claude Code, Agent Skills, Python',
      },
    ],
  },

  roles: [
    {
      period: '2022 - Present',
      location: 'Bucharest, Romania',
      position: 'Engineering Manager',
      company: 'nShift (formerly Consignor)',
      about: 'Global delivery-management platform: over 1,000 carriers across some 190 countries.',
      bullets: [
        {
          lead: 'Team leadership:',
          text: "lead the Webservices Team, one of nShift's core teams: set direction and engineering standards, including end-to-end test automation and CI/CD to AWS; own the architecture; hire and mentor.",
        },
      ],
      projects: [
        {
          name: 'nShift Companion, AI assistant',
          context:
            "a central piece of nShift's strategy for opening its products to customers through conversation. Built into the checkout, tracking, returns, audit and portal products, with an agent of its own for each product.",
          bullets: [
            {
              lead: 'Hybrid routing:',
              text: "designed the routing model. When the product is known, the embedded widget sends the request straight to that product's agent, with the user's original message and the full conversation history. It replaced an orchestrator-first design that reworded questions and lost context on follow-ups.",
            },
            {
              lead: 'Agent-to-agent delegation:',
              text: "built peer-to-peer delegation, so any agent can consult another product's agent through a shared tool. The list of available agents is built from the database at runtime, and a guard prevents agents from delegating in circles.",
            },
            {
              lead: 'Five production agents,',
              text: "built and shipped, each with product-specific prompts kept under version control, its own tool set and knowledge-base scope, and admin-managed starter questions (backend endpoints plus admin UI). I was the project's largest contributor over the year.",
            },
            {
              lead: 'Knowledge (RAG):',
              text: "imports the help-centre articles and keeps them in sync on a schedule, limits each agent to its own product's content, and cites the source articles in its answers.",
            },
            {
              lead: 'Actions, not just answers:',
              text: 'connected the agents to company systems through MCP, including invoicing and user management.',
            },
          ],
        },
        {
          name: 'Enterprise MCP Gateway',
          context:
            "the company's single, governed entry point between AI agents, nShift's own assistant and third-party agent platforms, and its systems, built on the open-source agentgateway. It fronts 8 tool servers across 6 product areas.",
          bullets: [
            {
              lead: 'Led design and build,',
              text: 'from the first commit to production.',
            },
            {
              lead: 'Access control:',
              text: 'every agent is identified and reaches only the systems and tools it is allowed to use; internal and external variants each publish their own catalogue.',
            },
            {
              lead: 'Existing APIs as AI tools:',
              text: 'published existing REST APIs as MCP tools without rewriting them, and connected tracking, checkout, user management, invoicing and pickup locations.',
            },
          ],
        },
        {
          name: 'Custom Price Calculation',
          context:
            "the new pricing engine behind nShift's self-service carrier rate cards. Customers keep their negotiated prices (zones, weight bands, surcharges, discounts) and get the exact cost of every shipment. It replaces the pricing engine I wrote in 2009.",
          bullets: [
            {
              lead: 'Engine and API:',
              text: 'main developer on a three-person team; designed the API as its own service and built most of its endpoints and the editor logic.',
            },
            {
              lead: 'Built for real agreements:',
              text: 'several price sheets per service, 16 ready-made templates, drafts, versions and publishing; one checked intake, with errors that name the exact line, so a rate card cannot go live half-valid.',
            },
            {
              lead: 'Migration:',
              text: 'own the move of existing customers from the legacy service, with regression tests that keep their prices identical.',
            },
            {
              lead: 'AI:',
              text: 'a proof of concept in which an agent edits a rate card from a plain-language instruction or builds one from an attached price list; now connecting the editor to nShift Companion.',
            },
          ],
        },
        {
          name: 'Address Lookup',
          context:
            "nShift's shared address service across many countries: autocomplete, validation, geocoding, reverse geocoding, postcode details, address splitting and distance. It powers pickup-point search at checkout.",
          bullets: [
            {
              lead: 'From proof of concept to platform:',
              text: 'designed and built it from the first commit; technical owner for three years, writing most of the code and guiding the developers and QA engineers who joined.',
            },
            {
              lead: 'Fast and fair under load:',
              text: 'in-memory search indexes for as-you-type speed, stress-tested before rollout, with per-client usage limits and a tracing ID that follows every request across services.',
            },
            {
              lead: 'Quality without the cost:',
              text: 'a licensed address dataset answers first, with a paid map service only as a fallback, and the data refreshes itself on a schedule.',
            },
          ],
        },
        {
          name: 'FileWatcher',
          context:
            'a background service installed on customer machines (Windows, Linux, macOS) that watches local folders and FTP, FTPS and SFTP servers and delivers every finished file to nShift reliably, even through network drops, restarts and updates.',
          bullets: [
            {
              lead: 'Lead development:',
              text: 'own the project and steer the developers on it, including an external contractor, from requirements to release.',
            },
            {
              lead: 'Management web app:',
              text: 'built most of the local management web UI and API: client accounts, profiles, endpoints, watch targets, settings, audit events and per-file processing status.',
            },
            {
              lead: 'Processing pipeline:',
              text: 'worked on detecting new files, checking that a file has stopped changing before sending it, uploading, and archiving per watch target. Delivery is at-least-once, and I added the deduplication key that lets the receiving side ignore repeats.',
            },
            {
              lead: 'Test environment:',
              text: 'built a test environment with SFTPGo (one user per protocol) and an end-to-end upload check.',
            },
          ],
        },
      ],
      tech: 'C#, .NET, ASP.NET Core, Python, FastAPI, SQL Server, PostgreSQL, React, TypeScript, Claude, AWS Bedrock, RAG, MCP, AWS (ECS, Fargate, RDS, S3, CDK), Docker, GitHub Actions, pytest, Playwright',
    },
    {
      period: '2017 - 2022',
      location: 'Bucharest, Romania',
      position: 'Team Manager',
      company: 'Consignor (formerly Edisoft)',
      about: "Scandinavia's leading multi-carrier shipping software; merged into nShift in 2021.",
      bullets: [
        {
          lead: 'Two teams at once:',
          text: 'led the Webservices Team, running the web services behind the Consignor client components, and the Integration Team, which brought Consignor into WooCommerce, Magento and Klarna.',
        },
        {
          lead: 'Architecture:',
          text: 'owned the design decisions across the Consignor suite: service boundaries, shared components and the data model.',
        },
        {
          lead: 'Cloud:',
          text: 'moved the platform on AWS from EC2 to Docker containers on ECS and Fargate, with CI/CD pipelines that deploy to them.',
        },
      ],
      tech: 'C#, .NET, ASP.NET Core, PHP, AWS (EC2, ECS, Fargate, S3, CloudFormation), Docker, Git, Prince2',
    },
    {
      period: '2010 - 2017',
      location: 'Bucharest, Romania',
      position: 'Technical Lead',
      company: 'Consignor (formerly Edisoft)',
      bullets: [
        {
          lead: 'Webservices Team:',
          text: 'led the team behind the 50 web services that served the Consignor suite; mentored and helped hire the developers who joined.',
        },
        {
          lead: 'Core applications:',
          text: 'built Routing Codes and Sending Edifacts, both still part of the nShift platform today.',
        },
      ],
      tech: 'C#, .NET, ASP.NET MVC, WCF, SQL Server, JavaScript, AWS (EC2, S3)',
    },
    {
      period: '2009 - 2010',
      location: 'Bucharest, Romania',
      position: 'Senior Software Engineer',
      company: 'Edisoft',
      bullets: [
        {
          lead: 'Custom Price Calculation Engine:',
          text: 'designed and built it. Customers upload the rates agreed with their carriers, and the engine prices every shipment from them. Written in 2009, still in production across nShift, and large enough that it grew its own team. I now lead its replacement (Custom Price Calculation, above).',
        },
      ],
      tech: 'C#, .NET, ASP.NET Web Forms, WCF, SQL Server',
    },
  ] as ResumeRole[],

  earlier: [
    {
      title: 'Senior Software Engineer | TeamNet',
      period: '2008 - 2009',
      text: 'owned Optimus ERP modules end to end, from specification to deployment. C#, .NET, SQL Server.',
    },
    {
      title: 'Game Programmer | Ubisoft',
      period: '2005 - 2008',
      text: "gameplay and platform modules for Silent Hunter 4, King Kong, Blazing Angels and Tom Clancy's FireHawk. C++.",
    },
  ],

  education: [
    {
      degree: 'MSc in Computer Science, Specialization in Project Management',
      school: 'Academy of Economic Studies, Bucharest',
      period: '2000 - 2002',
    },
    {
      degree: 'Bachelor in Business Administration, Major in Computer Science',
      school: 'Academy of Economic Studies, Bucharest',
      period: '1995 - 2000',
    },
  ],
};
