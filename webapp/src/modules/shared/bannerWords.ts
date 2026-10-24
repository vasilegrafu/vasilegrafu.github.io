// The banner's backdrop: terms from my own skills and projects, laid out as a
// wall of type. Generated once with a fixed seed and written down here rather
// than computed at render time -- the positions must be identical in the
// prerendered HTML and in the hydrated page, and a list of numbers cannot
// drift between them.
//
// The viewBox is 1200x96, the banner's own height, so slicing it to fit crops a
// few pixels rather than a whole row of words.
//
// Decorative only. The banner marks the whole thing aria-hidden, so none of
// this is read out or indexed as content.
export interface BannerWord {
  /** the term */
  t: string;
  /** position and size in the 1200x96 viewBox */
  x: number;
  y: number;
  s: number;
  /** font weight */
  w: number;
  /** fill opacity */
  o: number;
  /** true draws it darker than the gradient instead of lighter */
  d?: boolean;
}

export const bannerWords: BannerWord[] = [
  { t: 'Design Patterns', x: -7.7, y: 13.3, s: 9, w: 700, o: 0.28 },
  { t: 'Framework Design', x: 73.3, y: 13.3, s: 9, w: 600, o: 0.197 },
  { t: 'Prototype', x: 166.9, y: 13.3, s: 11, w: 400, o: 0.267 },
  { t: 'JavaScript', x: 231.3, y: 13.3, s: 11, w: 400, o: 0.107 },
  { t: 'AI-Assisted Development', x: 300.5, y: 13.3, s: 9, w: 500, o: 0.279 },
  { t: 'API Design', x: 420.8, y: 13.3, s: 13, w: 600, o: 0.33 },
  { t: 'EC2', x: 509.2, y: 13.3, s: 11, w: 500, o: 0.331 },
  { t: 'Agile', x: 541.2, y: 13.3, s: 16, w: 500, o: 0.323 },
  { t: 'Pipelines', x: 598.1, y: 13.3, s: 20, w: 400, o: 0.231 },
  { t: 'Mentoring', x: 702.7, y: 13.3, s: 13, w: 700, o: 0.258 },
  { t: 'REST', x: 781.1, y: 13.3, s: 9, w: 600, o: 0.333, d: true },
  { t: 'ReactJS', x: 821.8, y: 13.3, s: 9, w: 700, o: 0.169 },
  { t: 'MCP Servers', x: 864.8, y: 13.3, s: 26, w: 500, o: 0.238 },
  { t: 'CloudFormation', x: 1025.4, y: 13.3, s: 16, w: 600, o: 0.208 },
  { t: 'Razor', x: 1155.9, y: 13.3, s: 9, w: 600, o: 0.302, d: true },
  { t: 'Templates', x: -19.8, y: 27.2, s: 13, w: 500, o: 0.162 },
  { t: 'SQL Server', x: 59.8, y: 27.2, s: 26, w: 600, o: 0.153 },
  { t: 'SQL Server', x: 215.0, y: 27.2, s: 16, w: 500, o: 0.264, d: true },
  { t: 'ReactJS', x: 317.8, y: 27.2, s: 9, w: 500, o: 0.27 },
  { t: 'HTML', x: 364.6, y: 27.2, s: 11, w: 400, o: 0.334 },
  { t: 'Engineering Management', x: 410.3, y: 27.2, s: 11, w: 500, o: 0.335 },
  { t: 'Material UI', x: 548.3, y: 27.2, s: 9, w: 500, o: 0.187, d: true },
  { t: 'pytest', x: 623.3, y: 27.2, s: 11, w: 700, o: 0.319 },
  { t: 'Algorithms', x: 670.3, y: 27.2, s: 16, w: 700, o: 0.256 },
  { t: 'Jinja', x: 767.9, y: 27.2, s: 16, w: 500, o: 0.1 },
  { t: 'REST', x: 828.0, y: 27.2, s: 26, w: 700, o: 0.304 },
  { t: 'Data Structures', x: 899.9, y: 27.2, s: 20, w: 600, o: 0.087 },
  { t: 'Abstractions', x: 1071.6, y: 27.2, s: 26, w: 400, o: 0.275 },
  { t: 'pytest', x: -15.4, y: 43.9, s: 13, w: 500, o: 0.227, d: true },
  { t: 'CDK', x: 43.9, y: 43.9, s: 13, w: 600, o: 0.195 },
  { t: 'Mentoring', x: 84.5, y: 43.9, s: 13, w: 600, o: 0.244 },
  { t: 'Hiring', x: 168.6, y: 43.9, s: 11, w: 700, o: 0.334 },
  { t: 'Design Patterns', x: 221.2, y: 43.9, s: 11, w: 500, o: 0.296 },
  { t: '.NET', x: 324.7, y: 43.9, s: 26, w: 700, o: 0.116 },
  { t: 'HTML', x: 398.0, y: 43.9, s: 13, w: 600, o: 0.265, d: true },
  { t: 'Astro', x: 437.6, y: 43.9, s: 20, w: 500, o: 0.129 },
  { t: 'MCP Servers', x: 509.7, y: 43.9, s: 16, w: 500, o: 0.115 },
  { t: 'SOAP', x: 613.0, y: 43.9, s: 16, w: 500, o: 0.218 },
  { t: 'Templates', x: 661.9, y: 43.9, s: 9, w: 500, o: 0.134 },
  { t: 'ReactJS', x: 714.0, y: 43.9, s: 13, w: 700, o: 0.304 },
  { t: 'MCP Gateways', x: 780.1, y: 43.9, s: 20, w: 600, o: 0.096 },
  { t: 'Boundaries', x: 920.4, y: 43.9, s: 13, w: 600, o: 0.291 },
  { t: 'Clean Code', x: 1011.0, y: 43.9, s: 13, w: 700, o: 0.108 },
  { t: 'AWS', x: 1097.6, y: 43.9, s: 11, w: 400, o: 0.165 },
  { t: 'LINQ', x: 1124.8, y: 43.9, s: 13, w: 500, o: 0.158 },
  { t: 'CSS', x: 1170.8, y: 43.9, s: 16, w: 500, o: 0.203 },
  { t: 'Framework Design', x: -4.4, y: 60.3, s: 20, w: 600, o: 0.27 },
  { t: 'LLM Orchestration', x: 176.1, y: 60.3, s: 13, w: 600, o: 0.203 },
  { t: 'FastAPI', x: 308.6, y: 60.3, s: 26, w: 700, o: 0.136, d: true },
  { t: 'TypeScript', x: 415.4, y: 60.3, s: 9, w: 700, o: 0.214 },
  { t: 'MCP Gateways', x: 487.2, y: 60.3, s: 11, w: 700, o: 0.142, d: true },
  { t: 'pytest', x: 581.7, y: 60.3, s: 16, w: 700, o: 0.21 },
  { t: 'FastAPI', x: 655.7, y: 60.3, s: 9, w: 500, o: 0.151 },
  { t: 'pytest', x: 703.8, y: 60.3, s: 26, w: 400, o: 0.195 },
  { t: 'Abstractions', x: 806.9, y: 60.3, s: 11, w: 400, o: 0.071 },
  { t: 'LINQ', x: 896.5, y: 60.3, s: 26, w: 500, o: 0.074 },
  { t: 'Prototype', x: 967.4, y: 60.3, s: 26, w: 700, o: 0.302 },
  { t: 'AWS', x: 1106.7, y: 60.3, s: 13, w: 700, o: 0.294, d: true },
  { t: 'SASS', x: 1150.3, y: 60.3, s: 20, w: 600, o: 0.245 },
  { t: 'Calculus', x: -9.1, y: 75.5, s: 13, w: 500, o: 0.185 },
  { t: 'RDS', x: 55.7, y: 75.5, s: 13, w: 400, o: 0.284 },
  { t: 'CSS', x: 86.4, y: 75.5, s: 9, w: 700, o: 0.259, d: true },
  { t: 'Fargate', x: 123.9, y: 75.5, s: 20, w: 400, o: 0.262, d: true },
  { t: 'Astro', x: 211.4, y: 75.5, s: 11, w: 500, o: 0.235 },
  { t: 'ECS', x: 252.6, y: 75.5, s: 9, w: 400, o: 0.248 },
  { t: 'Prototype', x: 281.1, y: 75.5, s: 20, w: 400, o: 0.27 },
  { t: 'SASS', x: 386.8, y: 75.5, s: 9, w: 600, o: 0.255 },
  { t: 'Scrum', x: 421.2, y: 75.5, s: 9, w: 500, o: 0.258, d: true },
  { t: 'Statistics', x: 464.7, y: 75.5, s: 13, w: 500, o: 0.141 },
  { t: 'CI/CD', x: 546.4, y: 75.5, s: 20, w: 500, o: 0.288 },
  { t: 'JavaScript', x: 615.6, y: 75.5, s: 11, w: 500, o: 0.263 },
  { t: 'MCP Gateways', x: 684.2, y: 75.5, s: 9, w: 400, o: 0.207 },
  { t: 'Razor', x: 756.6, y: 75.5, s: 16, w: 600, o: 0.099 },
  { t: 'JavaScript', x: 816.9, y: 75.5, s: 9, w: 500, o: 0.325 },
  { t: 'Python', x: 886.4, y: 75.5, s: 9, w: 700, o: 0.292, d: true },
  { t: 'Mentoring', x: 934.5, y: 75.5, s: 11, w: 600, o: 0.16 },
  { t: 'JavaScript', x: 1001.5, y: 75.5, s: 16, w: 500, o: 0.265 },
  { t: 'SASS', x: 1099.5, y: 75.5, s: 13, w: 400, o: 0.23 },
  { t: 'TypeScript', x: 1148.3, y: 75.5, s: 9, w: 400, o: 0.08 },
  { t: 'Hiring', x: -1.9, y: 92.8, s: 9, w: 700, o: 0.197 },
  { t: 'CSS', x: 46.1, y: 92.8, s: 13, w: 700, o: 0.195 },
  { t: 'C#', x: 86.8, y: 92.8, s: 13, w: 700, o: 0.305 },
  { t: 'Python', x: 119.2, y: 92.8, s: 13, w: 500, o: 0.273 },
  { t: 'MCP Gateways', x: 170.3, y: 92.8, s: 13, w: 600, o: 0.155, d: true },
  { t: 'HTMX', x: 261.8, y: 92.8, s: 16, w: 500, o: 0.102 },
  { t: 'S3', x: 309.7, y: 92.8, s: 26, w: 500, o: 0.079 },
  { t: '.NET', x: 355.9, y: 92.8, s: 20, w: 700, o: 0.316 },
  { t: 'SOAP', x: 418.4, y: 92.8, s: 16, w: 600, o: 0.146 },
  { t: 'Framework Design', x: 473.2, y: 92.8, s: 11, w: 500, o: 0.251 },
  { t: 'SASS', x: 585.0, y: 92.8, s: 26, w: 600, o: 0.072, d: true },
  { t: 'Material UI', x: 661.6, y: 92.8, s: 11, w: 400, o: 0.079 },
  { t: 'Components', x: 747.9, y: 92.8, s: 13, w: 400, o: 0.263 },
  { t: 'ASP.NET Core', x: 838.3, y: 92.8, s: 16, w: 400, o: 0.254 },
  { t: 'Neural Networks', x: 956.1, y: 92.8, s: 9, w: 600, o: 0.295 },
  { t: 'MCP Gateways', x: 1046.6, y: 92.8, s: 11, w: 500, o: 0.258 },
  { t: 'RDS', x: 1128.2, y: 92.8, s: 9, w: 600, o: 0.284, d: true },
  { t: 'Framework Design', x: 1168.0, y: 92.8, s: 20, w: 400, o: 0.301 },
];
