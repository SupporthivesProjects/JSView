import { Group, Modal } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useCallback } from 'react';

import { StylishText } from '@lib/components/StylishText';
import type { UseModalProps, UseModalReturn } from '@lib/types/Modals';
import { useUserSettingsState } from '@store/SettingsStates';

export function useModal(props: UseModalProps): UseModalReturn {
  const onOpen = useCallback(() => {
    props.onOpen?.();
  }, [props.onOpen]);

  const userSettings = useUserSettingsState();

  const onClose = useCallback(() => {
    props.onClose?.();
  }, [props.onClose]);

  const [opened, { open, close, toggle }] = useDisclosure(false, {
    onOpen,
    onClose
  });

  return {
    open,
    close,
    toggle,
    modal: (
      <Modal
        key={props.id}
        opened={opened}
        closeOnEscape={userSettings.isSet('FORMS_CLOSE_USING_ESCAPE')}
        onClose={close}
        closeOnClickOutside={props.closeOnClickOutside}
        size={props.size ?? 'xl'}
        // The title spans the header, so that anything passed alongside it
        // sits at the right hand side (just before the close button)
        styles={{ title: { flex: 1 } }}
        title={
          <Group justify='space-between' wrap='nowrap' gap='sm'>
            <StylishText size='xl'>{props.title}</StylishText>
            {props.titleActions}
          </Group>
        }
      >
        {props.children}
      </Modal>
    )
  };
}
