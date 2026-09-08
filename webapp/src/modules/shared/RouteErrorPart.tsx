// What the router shows when a page fails to render or load, instead of its
// default "Unexpected Application Error!" screen.
import { useLocation, useRouteError } from 'react-router';
import PageMetaPart from './PageMetaPart';

export default function RouteErrorPart() {
  const error = useRouteError();
  const { pathname } = useLocation();
  const message = error instanceof Error ? error.message : String(error);
  return (
    <div className="mx-auto max-w-7xl px-4 py-20 text-center sm:px-6 lg:px-8">
      <PageMetaPart title="Something went wrong — Vasile Grafu" noindex />
      <h1 className="title-page">Something went wrong</h1>
      <p className="text-muted mt-4">This page could not be loaded.</p>
      <p className="text-faint mt-2">{message}</p>
      <a href={pathname} className="link-accent mt-6 inline-block">
        Reload the page
      </a>
    </div>
  );
}
