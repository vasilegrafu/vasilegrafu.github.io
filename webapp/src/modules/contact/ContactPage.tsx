import IconPart from '@fx/components/IconPart';
import LinkCardPart from '@fx/components/LinkCardPart';
import PageMetaPart from '@modules/shared/PageMetaPart';
import { site } from '@data/profile';

export default function ContactPage() {
  return (
    <>
      <PageMetaPart
        title="Contact — Vasile Grafu"
        description="Get in touch with Vasile Grafu to exchange ideas on engineering leadership, AI systems, and research."
      />

      <div className="relative">
        <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden" aria-hidden="true">
          <div className="blob bg-blob-a -top-16 -right-24 h-72 w-72"></div>
          <div className="blob bg-blob-b top-48 -left-24 h-56 w-56"></div>
        </div>

        <h1 className="title-page">Contact</h1>
        <p className="lede">I read everything and reply to thoughtful messages.</p>

        {/* minmax(0, …): the link cards truncate their subtitle, and a plain
            auto/1fr track would refuse to shrink below that untruncated width. */}
        <div className="mt-8 grid grid-cols-[minmax(0,1fr)] gap-8 lg:grid-cols-[minmax(0,1fr)_20rem]">
          <div className="space-y-4">
            <LinkCardPart
              href={`mailto:${site.email}`}
              icon="lucide:mail"
              title="Email"
              subtitle={site.email}
            />
            <LinkCardPart
              href={site.linkedin}
              icon="lucide:linkedin"
              title="LinkedIn"
              subtitle="Best for professional messages"
            />
            <LinkCardPart
              href={site.github}
              icon="lucide:github"
              title="GitHub"
              subtitle="Code and experiments"
            />
          </div>

          <aside className="card bg-tint h-fit p-6">
            <ul className="text-muted space-y-4">
              <li className="flex items-start gap-3">
                <IconPart name="lucide:map-pin" className="text-label mt-0.5 h-4 w-4 shrink-0" />
                <span>{site.location}</span>
              </li>
              <li className="flex items-start gap-3">
                <IconPart name="lucide:clock" className="text-label mt-0.5 h-4 w-4 shrink-0" />
                <span>EET (UTC+2)</span>
              </li>
            </ul>
          </aside>
        </div>
      </div>
    </>
  );
}
