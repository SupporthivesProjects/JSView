import { t } from '@lingui/core/macro';
import { Stack } from '@mantine/core';
import { useMemo } from 'react';

import { StylishText } from '@lib/components/StylishText';
import { DocumentationLinks } from '@config/links';
import { GettingStartedCarousel } from '../../../ui/items/GettingStartedCarousel';
import type { MenuLinkItem } from '../../../ui/items/MenuLinks';

export default function GetStartedWidget() {
  const docLinks: MenuLinkItem[] = useMemo(() => DocumentationLinks(), []);

  return (
    <Stack>
      <StylishText size='xl'>{t`Getting Started`}</StylishText>
      <GettingStartedCarousel items={docLinks} />
    </Stack>
  );
}
