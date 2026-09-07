// The browser router. Kept apart from routeTree.tsx because creating it
// touches window, which the build-time prerenderer does not have.
import { createBrowserRouter } from 'react-router';
import { routeObjects } from './routeTree';

export const router = createBrowserRouter(routeObjects);
