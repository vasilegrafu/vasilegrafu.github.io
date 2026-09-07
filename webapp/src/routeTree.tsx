// The route objects React Router renders, built from the manifest in
// routes.ts. Shared by the browser router (router.tsx) and the build-time
// prerenderer (prerender.tsx). Each page is a lazy chunk; BaseLayout renders
// them inside its Suspense boundary, and `bare` routes render on their own
// outside the shell.
import { lazy, Suspense, type ComponentType, type LazyExoticComponent } from 'react';
import { Navigate, type RouteObject } from 'react-router';
import BaseLayout from '@modules/shared/BaseLayout';
import { redirects, routes, type PageId } from './routes';

const pages: Record<PageId, LazyExoticComponent<ComponentType>> = {
  index: lazy(() => import('@modules/index/IndexPage')),
  career: lazy(() => import('@modules/career/CareerPage')),
  skills: lazy(() => import('@modules/skills/SkillsPage')),
  projects: lazy(() => import('@modules/projects/ProjectsPage')),
  articles: lazy(() => import('@modules/articles/ArticlesPage')),
  article: lazy(() => import('@modules/articles/ArticlePage')),
  contact: lazy(() => import('@modules/contact/ContactPage')),
  'resume-print': lazy(() => import('@modules/resume-print/ResumePrintPage')),
  'not-found': lazy(() => import('@modules/404/NotFoundPage')),
};

const toRoute = (path: string, page: PageId): RouteObject => {
  const Page = pages[page];
  return { path, element: <Page /> };
};

const shellRoutes = routes.filter((r) => !r.bare);
const bareRoutes = routes.filter((r) => r.bare);

export const routeObjects: RouteObject[] = [
  {
    element: <BaseLayout />,
    children: [
      ...shellRoutes.map((r) => toRoute(r.path, r.page)),
      ...redirects.map((r) => ({ path: r.from, element: <Navigate to={r.to} replace /> })),
    ],
  },
  ...bareRoutes.map((r) => {
    const Page = pages[r.page];
    return {
      path: r.path,
      element: (
        <Suspense>
          <Page />
        </Suspense>
      ),
    };
  }),
];
