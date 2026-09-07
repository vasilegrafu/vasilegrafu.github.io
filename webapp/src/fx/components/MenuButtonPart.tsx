// Hamburger button that opens/closes a mobile menu panel; the panel state
// lives in the parent.
import IconPart from './IconPart';

interface Props {
  open: boolean;
  onToggle: () => void;
  /** id of the panel this button controls, for aria-controls. */
  controls?: string;
}

export default function MenuButtonPart({ open, onToggle, controls }: Props) {
  return (
    <button
      type="button"
      aria-label={open ? 'Close menu' : 'Open menu'}
      aria-expanded={open}
      aria-controls={controls}
      onClick={onToggle}
      className="border-line-strong text-ink hover:border-accent hover:text-accent inline-flex h-9 w-9 items-center justify-center rounded-lg border transition-colors sm:hidden"
    >
      <IconPart name={open ? 'lucide:x' : 'lucide:menu'} className="h-5 w-5" />
    </button>
  );
}
