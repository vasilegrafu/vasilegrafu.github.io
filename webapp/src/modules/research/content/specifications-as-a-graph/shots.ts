// The tour of the application, in the order a first visit takes.
//
// You start on the front page and open the whole graph; then you follow one
// requirement through its links, its tests and the screens that show it; the
// last two show what a change looks like from the inside.
//
// It lives in its own file because three places need the same list in the same
// order: the gallery that lays it out, the thumbnails beside the title, and the
// viewer, which lets a reader walk the whole set from wherever they came in.
import { asset } from './assets';
import type { Shot } from './GalleryPart';
import type { Pic } from '@fx/components/ViewerPart';

export const SHOTS: Shot[] = [
  {
    name: 'overview.png',
    kicker: 'Document',
    title: 'The front page',
    alt: 'The front page of the Voltline specification',
    caption:
      'Where every reader starts. What the product is, how big the specification is, and what is still open.',
  },
  {
    name: 'graph.png',
    kicker: 'Graph',
    title: 'The whole specification',
    alt: 'The graph view, with one bubble per kind of node',
    caption:
      'Each bubble is one kind of node, sized by how many there are. Each line shows how many links join two kinds.',
  },
  {
    name: 'graph-card.png',
    kicker: 'Graph',
    title: 'A right-click opens a card',
    alt: 'A summary card for one node, opened from the graph',
    caption:
      'A short summary without leaving the graph. Every ID in the card opens the next card, so you can walk from fact to fact.',
  },
  {
    name: 'layers.png',
    kicker: 'Graph',
    title: 'The layers',
    alt: 'Every node arranged in layers, goals on the left and components on the right',
    caption:
      'All of it in layers, goals on the left and components on the right. You can follow one goal to every part that serves it.',
  },
  {
    name: 'layers-flow.png',
    kicker: 'Graph',
    title: 'The layers of one flow',
    alt: 'The layer view narrowed to a single flow',
    caption:
      'One flow — buying a product — selected. Only the goals, requirements, endpoints and screens that flow uses.',
  },
  {
    name: 'requirement.png',
    kicker: 'Requirements',
    title: 'One requirement',
    alt: 'Requirement R4 in full, with its evidence and open question',
    caption:
      'R4 in full: what it says, where it came from, how sure the specification is, and the question still open about it.',
  },
  {
    name: 'criteria.png',
    kicker: 'Requirements',
    title: 'Its tests, in plain words',
    alt: 'Acceptance criteria written as given, when, then',
    caption:
      'Each acceptance criterion is given, when, then. Builder agents turn these lines straight into automated tests.',
  },
  {
    name: 'design.png',
    kicker: 'Design',
    title: 'The design system',
    alt: 'The design system: colours, fonts and spacing',
    caption:
      'The colours, fonts and spacing every screen follows. Agents read the same thing as a file of design tokens.',
  },
  {
    name: 'prototype.png',
    kicker: 'Design',
    title: 'A working prototype',
    alt: 'A working prototype of a product page',
    caption:
      'A real page, built from the screen’s description and the design system. Viewable at phone, tablet or desktop size.',
  },
  {
    name: 'wireframe.png',
    kicker: 'Design',
    title: 'Every element explained',
    alt: 'The same page with every element labelled',
    caption:
      'The same page with every element labelled: which component it is, and which requirement it serves.',
  },
  {
    name: 'inspector.png',
    kicker: 'Design',
    title: 'One element, inspected',
    alt: 'The inspector open on the quantity field of the product page',
    caption:
      'The quantity field, on the live page: the requirement it shows, the rule and evidence behind it, and what it says — a number from 1 to 5. This is where the change in this article arrives.',
  },
  {
    name: 'matrix.png',
    kicker: 'Matrix',
    title: 'What links to what',
    alt: 'A matrix of every kind of node against every other kind',
    caption:
      'Every kind of node against every other, each cell counting the links. An empty cell is often a gap.',
  },
  {
    name: 'stale.png',
    kicker: 'Change',
    title: 'After a change, what needs review',
    alt: 'The list of nodes that need review after a change',
    caption:
      'Five became six. Everything that depends on what changed is listed, with the old and the new words, until someone reviews it.',
  },
];

/** The same list as the viewer wants it: a picture and what it shows. */
export const PICS: Pic[] = SHOTS.map((s) => ({ src: asset(s.name), alt: s.alt }));

/** Where a named shot sits in the tour, for opening the viewer on it. */
export const indexOfShot = (name: string) => SHOTS.findIndex((s) => s.name === name);
