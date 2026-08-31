export const site = {
  name: 'Vasile Grafu',
  title: 'Engineering Manager | Solutions Architect | Enterprise & AI Systems',
  tagline:
    'Engineering leader with 20+ years in software — from game programming at Ubisoft to cloud platforms handling millions of requests a day, now building agentic AI systems.',
  location: 'Bucharest, Romania',
  email: 'vasilegrafu@gmail.com',
  phone: '+40 722 635 785',
  linkedin: 'https://www.linkedin.com/in/vasile-grafu-6a99369',
  github: 'https://github.com/vasilegrafu',
  url: 'https://vasilegrafu.github.io',
};

export interface Role {
  company: string;
  position: string;
  period: string;
  location: string;
  summary: string;
  bullets: string[];
  tech?: string[];
}

export const experience: Role[] = [
  {
    company: 'nShift (formerly Consignor)',
    position: 'Engineering Manager',
    period: 'January 2022 – Present',
    location: 'Bucharest, Romania',
    summary:
      'nShift is a global leader in parcel delivery management and multi-carrier shipping software. I lead the Webservices Team — one of the company’s core teams — building web services that handle millions of requests per day and support multiple business-critical applications. I combine hands-on development with leadership: contributing to coding, architecture, and decision-making while ensuring alignment across teams.',
    bullets: [
      'Lead and manage the Webservices Team: setting clear goals, providing direction, and keeping every member motivated and effective.',
      'Establish engineering processes and standards — consistent development practices that improve collaboration, maintain quality, and accelerate delivery.',
      'Recruit and develop engineers: active role in hiring, onboarding, and mentoring to build a skilled, cohesive team.',
      'Provide technical guidance: solving complex issues alongside developers, reviewing designs, and making critical decisions on challenging topics.',
      'Contribute to software architecture: design and implementation of scalable, secure, and maintainable systems.',
      'Hands-on development: shared components, application structure, data flow, database design, security principles, and infrastructure improvements.',
      'Solution Architect for our applications: designing and managing cloud environments on AWS and implementing CI/CD pipelines.',
      'Act as Scrum Master: stand-ups, planning, retrospectives, and effective communication between Product Owners and developers.',
      'Building a large-scale internal conversational AI platform: LLMs, agent orchestration, RAG, and MCP-style tool integration.',
    ],
    tech: [
      'AI-assisted development',
      'C# / .NET / ASP.NET Core',
      'Python / FastAPI / SQLAlchemy',
      'SQL Server / PostgreSQL',
      'AWS (EC2, ECS, RDS, S3)',
      'Docker',
      'JavaScript / ReactJS / Material UI',
    ],
  },
  {
    company: 'Consignor',
    position: 'Team Manager',
    period: 'January 2017 – January 2022',
    location: 'Bucharest, Romania',
    summary:
      'Consignor, a Scandinavian company with offices in Norway, Denmark, and Sweden, was the largest supplier of transport administration solutions in Scandinavia. I led two teams and wore the hat each situation demanded: Team Manager, Technical Lead, Project Manager (Prince2), or Software Developer.',
    bullets: [
      'Webservices Team: ran the web services serving the client components of the Consignor business.',
      'Integration Team: brought Consignor functionality to the major e-commerce platforms.',
      'Hiring, training, and coordinating people; critical architecture decisions; hands-on development; and management of cross-team projects.',
    ],
  },
  {
    company: 'Consignor',
    position: 'Technical Lead',
    period: '2009 – 2017',
    location: 'Bucharest, Romania',
    summary:
      'Led the team behind 50 web services and 5 full-stack web applications serving over 10,000 business clients in the Consignor application suite, distributed across Amazon Cloud.',
    bullets: [
      'Key part of the entire application development workflow.',
      'Designed many modules of the business software to satisfy client requirements.',
      'Mentored junior and senior developers.',
      'Wrote detailed technical and user documentation.',
      'Acted as liaison between the development team and other departments.',
    ],
    tech: [
      'C# .NET, ASP.NET MVC',
      'WCF',
      'SQL Server Enterprise',
      'JavaScript, jQuery, Bootstrap, LESS/SASS',
      'Python, IronPython',
      'Amazon Web Services',
    ],
  },
  {
    company: 'TeamNet',
    position: 'Team Leader',
    period: '2008 – 2009',
    location: 'Bucharest, Romania',
    summary:
      'TeamNet offered software development and implementation services for the business segment of the market.',
    bullets: [
      'Managed the Optimus ERP modules through all development steps, from specification to testing and deployment.',
      'Elaborated development plans for new features in collaboration with the design department.',
      'Responsible for enhancing existing features and for triaging and resolving all defects identified by the Quality Department.',
    ],
  },
  {
    company: 'Ubisoft',
    position: 'Game Programmer',
    period: 'January 2005 – June 2008',
    location: 'Bucharest, Romania',
    summary:
      'Ubisoft is one of the leading game publishers worldwide. I designed, developed, and optimized gameplay and platform modules on four shipped and in-development titles.',
    bullets: [
      'Silent Hunter 4: designed and built the framework managing the evolution of the Crew, Weapons, and Equipment of the U-Boat simulator, plus the Career module.',
      'King Kong (PC): Intel Viiv / Windows Media Center integration, multithreaded rendering, and the security module.',
      'Blazing Angels (PC): Save/Load system and Media Center shell implementation.',
      'Tom Clancy’s FireHawk: ERS (Enhanced Reality System) module.',
    ],
    tech: ['C++, STL', 'Software optimization', 'Linear algebra, calculus, probabilities'],
  },
];

export const skills: { group: string; items: string[] }[] = [
  {
    group: 'Leadership & Management',
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
    group: 'AI & Machine Learning',
    items: [
      'AI-Assisted Software Development',
      'Agentic Architectures & LLM Orchestration',
      'RAG (Retrieval-Augmented Generation)',
      'Prompt Engineering & MCP-style Tool Integration',
      'Machine Learning & Deep Learning (TensorFlow, NumPy, Pandas)',
      'Probability, Linear Algebra, Calculus, Statistics',
    ],
  },
  {
    group: 'Backend & Architecture',
    items: [
      'C#, .NET, ASP.NET Core, Entity Framework, LINQ',
      'Python, FastAPI, SQLAlchemy',
      'Solution & Software Architecture',
      'Framework Design',
      'Data Structures & Algorithms',
    ],
  },
  {
    group: 'Cloud & Data',
    items: [
      'AWS (EC2, ECS, RDS, S3, CloudFormation)',
      'Docker, CI/CD',
      'SQL Server, PostgreSQL',
      'Database Design, Relational Databases',
    ],
  },
  {
    group: 'Frontend',
    items: ['JavaScript, ReactJS', 'HTML, CSS, SASS', 'Material UI'],
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

export const selfLearning =
  'I have a strong curiosity-driven mindset that extends beyond formal job requirements and continuously pushes me to deepen my understanding of computer science and AI. Over time this has led me to independently build a solid conceptual foundation in machine learning, deep learning, neural networks, reinforcement learning, probability theory, linear algebra, calculus, and statistics. I prioritize understanding core principles and mathematical foundations — developing deep intuition for how algorithms and systems work under the hood — which lets me reason effectively about system design, model behavior, and trade-offs in complex technical environments. Along the way I have worked hands-on with Python, NumPy, Pandas, TensorFlow, and Matplotlib in practical experiments and small-scale implementations.';

export interface Project {
  title: string;
  role: string;
  description: string;
  tags: string[];
}

export const projects: Project[] = [
  {
    title: 'Internal Conversational AI Platform',
    role: 'Engineering Manager & Architect · nShift',
    description:
      'A large-scale internal AI assistant built on an agentic architecture: LLMs combined with orchestration layers, RAG, and structured prompt engineering. Domain-specific agents for different departments — each with tailored prompts, tools, and data access — collaborate through an orchestration layer. A continuous ingestion pipeline indexes internal documentation, APIs, and business data into knowledge stores, so responses stay context-aware and grounded in company-specific information.',
    tags: ['LLMs', 'Agents', 'RAG', 'MCP', 'Orchestration', 'Python'],
  },
  {
    title: 'High-Throughput Webservices Platform',
    role: 'Engineering Manager · nShift',
    description:
      'The core web-services platform behind nShift’s delivery-management suite: dozens of services and full-stack applications distributed across AWS, serving the client components of business-critical delivery workflows around the clock.',
    tags: ['C# / .NET', 'AWS', 'SQL Server', 'PostgreSQL', 'Docker', 'CI/CD'],
  },
  {
    title: 'E-Commerce Platform Integrations',
    role: 'Team Manager · Consignor',
    description:
      'Led the team that brought Consignor’s shipping functionality into major e-commerce ecosystems — WooCommerce, Klarna, Magento, and more — connecting thousands of online shops to multi-carrier delivery.',
    tags: ['Integrations', 'E-commerce', 'APIs'],
  },
];
