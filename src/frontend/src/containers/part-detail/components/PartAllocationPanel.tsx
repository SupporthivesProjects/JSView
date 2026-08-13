import { t } from '@lingui/core/macro';
import { Accordion } from '@mantine/core';

import { StylishText } from '@lib/components/StylishText';
import { UserRoles } from '@lib/enums/Roles';
import { useUserState } from '@store/UserState';
import PartBuildAllocationsTable from '@components/tables/part/PartBuildAllocationsTable';
import PartSalesAllocationsTable from '@components/tables/part/PartSalesAllocationsTable';

export default function PartAllocationPanel({ part }: Readonly<{ part: any }>) {
  const user = useUserState();

  return (
    <Accordion
      multiple={true}
      defaultValue={['buildallocations', 'salesallocations']}
    >
      {part.component && user.hasViewRole(UserRoles.build) && (
        <Accordion.Item value='buildallocations' key='buildallocations'>
          <Accordion.Control>
            <StylishText size='lg'>{t`Build Order Allocations`}</StylishText>
          </Accordion.Control>
          <Accordion.Panel>
            <PartBuildAllocationsTable partId={part.pk} />
          </Accordion.Panel>
        </Accordion.Item>
      )}
      {part.salable && user.hasViewRole(UserRoles.sales_order) && (
        <Accordion.Item value='salesallocations' key='salesallocations'>
          <Accordion.Control>
            <StylishText size='lg'>{t`Sales Order Allocations`}</StylishText>
          </Accordion.Control>
          <Accordion.Panel>
            <PartSalesAllocationsTable partId={part.pk} />
          </Accordion.Panel>
        </Accordion.Item>
      )}
    </Accordion>
  );
}
