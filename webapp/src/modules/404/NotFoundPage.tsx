import { Link } from 'react-router';
import PageMetaPart from '@modules/shared/PageMetaPart';

export default function NotFoundPage() {
  return (
    <>
      <PageMetaPart title="Page not found — Vasile Grafu" noindex />
      <div className="py-20 text-center">
        <h1 className="title-hero">404</h1>
        <p className="text-muted mt-4">This page doesn’t exist.</p>
        <Link to="/" className="link-accent mt-6 inline-block">
          ← Back home
        </Link>
      </div>
    </>
  );
}
