import type { UiSizeType } from './Core';

export interface UseModalProps {
  id: string;
  title: string;
  /** Optional content rendered at the right hand side of the modal header,
   *  alongside the close button (e.g. an actions dropdown) */
  titleActions?: React.ReactNode;
  children: React.ReactElement;
  size?: UiSizeType;
  onOpen?: () => void;
  onClose?: () => void;
  closeOnClickOutside?: boolean;
}

export interface UseModalReturn {
  open: () => void;
  close: () => void;
  toggle: () => void;
  modal: React.ReactElement;
}
