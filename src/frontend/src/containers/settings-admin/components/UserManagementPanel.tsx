import { t } from '@lingui/core/macro';
import { Accordion } from '@mantine/core';

import { StylishText } from '@lib/components/StylishText';
import { GlobalSettingList } from '@components/shared/settings/SettingList';
import { ApiTokenTable } from '@components/tables/settings/ApiTokenTable';
import { GroupTable } from '@components/tables/settings/GroupTable';
import { UserTable } from '@components/tables/settings/UserTable';

export default function UserManagementPanel() {
  return (
    <Accordion multiple defaultValue={['users']}>
      <Accordion.Item value='users' key='users'>
        <Accordion.Control>
          <StylishText size='lg'>{t`Users`}</StylishText>
        </Accordion.Control>
        <Accordion.Panel>
          <UserTable />
        </Accordion.Panel>
      </Accordion.Item>
      <Accordion.Item value='groups' key='groups'>
        <Accordion.Control>
          <StylishText size='lg'>{t`Groups`}</StylishText>
        </Accordion.Control>
        <Accordion.Panel>
          <GroupTable />
        </Accordion.Panel>
      </Accordion.Item>
      <Accordion.Item value='tokens' key='tokens'>
        <Accordion.Control>
          <StylishText size='lg'>{t`Tokens`}</StylishText>
        </Accordion.Control>
        <Accordion.Panel>
          <ApiTokenTable only_myself={false} />
        </Accordion.Panel>
      </Accordion.Item>
      <Accordion.Item value='settings' key='settings'>
        <Accordion.Control>
          <StylishText size='lg'>{t`Settings`}</StylishText>
        </Accordion.Control>
        <Accordion.Panel>
          <GlobalSettingList
            keys={['LOGIN_ENABLE_REG', 'SIGNUP_GROUP', 'LOGIN_ENABLE_SSO_REG']}
          />
        </Accordion.Panel>
      </Accordion.Item>
    </Accordion>
  );
}
