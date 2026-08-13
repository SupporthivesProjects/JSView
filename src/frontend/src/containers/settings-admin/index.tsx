import { PluginPanelKey } from '@lib/enums/ModelType';
import { UserRoles } from '@lib/enums/Roles';
import type { PanelGroupType, PanelType } from '@lib/types/Panel';
import { t } from '@lingui/core/macro';
import { Stack } from '@mantine/core';
import {
  IconCoins,
  IconCpu,
  IconDevicesPc,
  IconExclamationCircle,
  IconFileCode,
  IconFileDownload,
  IconFileUpload,
  IconHome,
  IconList,
  IconListDetails,
  IconMail,
  IconPackages,
  IconPhoto,
  IconPlugConnected,
  IconQrcode,
  IconReport,
  IconScale,
  IconSitemap,
  IconTags,
  IconUsersGroup
} from '@tabler/icons-react';
import { lazy, useMemo } from 'react';
import PermissionDenied from '@components/shared/errors/PermissionDenied';
import PageTitle from '@components/nav/PageTitle';
import { SettingsHeader } from '@components/nav/SettingsHeader';
import { PanelGroup } from '@components/shared/panels/PanelGroup';
import { GlobalSettingList } from '@components/shared/settings/SettingList';
import { Loadable } from '@helpers/loading';
import { useUserState } from '@store/UserState';
import ParameterTemplateTable from '@components/tables/general/ParameterTemplateTable';
import SelectionListTable from '@components/tables/settings/SelectionListTable';

const ReportTemplatePanel = Loadable(
  lazy(() => import('./components/ReportTemplatePanel'))
);

const LabelTemplatePanel = Loadable(lazy(() => import('./components/LabelTemplatePanel')));

const HomePanel = Loadable(lazy(() => import('./components/HomePanel')));

const UserManagementPanel = Loadable(
  lazy(() => import('./components/UserManagementPanel'))
);

const EmailManagementPanel = Loadable(
  lazy(() => import('./components/EmailManagementPanel'))
);

const TaskManagementPanel = Loadable(
  lazy(() => import('./components/TaskManagementPanel'))
);

const CurrencyManagementPanel = Loadable(
  lazy(() => import('./components/CurrencyManagementPanel'))
);

const UnitManagementPanel = Loadable(
  lazy(() => import('./components/UnitManagementPanel'))
);

const PluginManagementPanel = Loadable(
  lazy(() => import('./components/PluginManagementPanel'))
);

const MachineManagementPanel = Loadable(
  lazy(() => import('./components/MachineManagementPanel'))
);

const ErrorReportTable = Loadable(
  lazy(() => import('@components/tables/settings/ErrorTable'))
);

const BarcodeScanHistoryTable = Loadable(
  lazy(() => import('@components/tables/settings/BarcodeScanHistoryTable'))
);

const ExportSessionTable = Loadable(
  lazy(() => import('@components/tables/settings/ExportSessionTable'))
);

const ImportSessionTable = Loadable(
  lazy(() => import('@components/tables/settings/ImportSessionTable'))
);

const ProjectCodeTable = Loadable(
  lazy(() => import('@components/tables/settings/ProjectCodeTable'))
);

const CustomStateTable = Loadable(
  lazy(() => import('@components/tables/settings/CustomStateTable'))
);

const PartCategoryTemplateTable = Loadable(
  lazy(() => import('@components/tables/part/PartCategoryTemplateTable'))
);

const LocationTypesTable = Loadable(
  lazy(() => import('@components/tables/stock/LocationTypesTable'))
);

const SnippetTable = Loadable(
  lazy(() => import('@components/tables/settings/SnippetTable'))
);

const AssetTable = Loadable(
  lazy(() => import('@components/tables/settings/AssetTable'))
);

export default function AdminCenter() {
  const user = useUserState();

  const adminCenterPanels: PanelType[] = useMemo(() => {
    return [
      {
        name: 'home',
        label: t`Home`,
        icon: <IconHome />,
        content: <HomePanel />,
        showHeadline: false
      },
      {
        name: 'user',
        label: t`Users / Access`,
        icon: <IconUsersGroup />,
        content: <UserManagementPanel />,
        hidden: !user.hasViewRole(UserRoles.admin)
      },
      {
        name: 'email',
        label: t`Email Settings`,
        icon: <IconMail />,
        content: <EmailManagementPanel />,
        hidden: !user.isSuperuser()
      },
      {
        name: 'import',
        label: t`Data Import`,
        icon: <IconFileUpload />,
        content: <ImportSessionTable />
      },
      {
        name: 'export',
        label: t`Data Export`,
        icon: <IconFileDownload />,
        content: <ExportSessionTable />
      },
      {
        name: 'barcode-history',
        label: t`Barcode Scans`,
        icon: <IconQrcode />,
        content: <BarcodeScanHistoryTable />
      },
      {
        name: 'background',
        label: t`Background Tasks`,
        icon: <IconCpu />,
        content: <TaskManagementPanel />
      },
      {
        name: 'errors',
        label: t`Error Reports`,
        icon: <IconExclamationCircle />,
        content: <ErrorReportTable />
      },
      {
        name: 'currencies',
        label: t`Currencies`,
        icon: <IconCoins />,
        content: <CurrencyManagementPanel />
      },
      {
        name: 'project-codes',
        label: t`Project Codes`,
        icon: <IconListDetails />,
        content: (
          <Stack gap='xs'>
            <GlobalSettingList keys={['PROJECT_CODES_ENABLED']} />
            <ProjectCodeTable />
          </Stack>
        )
      },
      {
        name: 'custom-states',
        label: t`Custom States`,
        icon: <IconListDetails />,
        content: <CustomStateTable />
      },
      {
        name: 'custom-units',
        label: t`Custom Units`,
        icon: <IconScale />,
        content: <UnitManagementPanel />
      },
      {
        name: 'parameters',
        label: t`Parameters`,
        icon: <IconList />,
        content: <ParameterTemplateTable />,
        hidden: !user.hasViewRole(UserRoles.part)
      },
      {
        name: 'selection-lists',
        label: t`Selection Lists`,
        icon: <IconList />,
        content: <SelectionListTable />,
        hidden: !user.hasViewRole(UserRoles.part)
      },
      {
        name: 'category-parameters',
        label: t`Category Parameters`,
        icon: <IconSitemap />,
        content: <PartCategoryTemplateTable />,
        hidden: !user.hasViewRole(UserRoles.part_category)
      },
      {
        name: 'labels',
        label: t`Label Templates`,
        icon: <IconTags />,
        content: <LabelTemplatePanel />
      },
      {
        name: 'reports',
        label: t`Report Templates`,
        icon: <IconReport />,
        content: <ReportTemplatePanel />
      },
      {
        name: 'snippets',
        label: t`Report Snippets`,
        icon: <IconFileCode />,
        content: <SnippetTable />
      },
      {
        name: 'assets',
        label: t`Report Assets`,
        icon: <IconPhoto />,
        content: <AssetTable />
      },
      {
        name: 'location-types',
        label: t`Location Types`,
        icon: <IconPackages />,
        content: <LocationTypesTable />,
        hidden: !user.hasViewRole(UserRoles.stock_location)
      },
      {
        name: 'plugin',
        label: t`Plugins`,
        icon: <IconPlugConnected />,
        content: <PluginManagementPanel />,
        hidden: !user.hasViewRole(UserRoles.admin)
      },
      {
        name: 'machine',
        label: t`Machines`,
        icon: <IconDevicesPc />,
        content: <MachineManagementPanel />,
        hidden: !user.hasViewRole(UserRoles.admin)
      }
    ];
  }, [user]);
  const grouping: PanelGroupType[] = useMemo(() => {
    return [
      { id: 'home', label: '', panelIDs: ['home'] },
      {
        id: 'ops',
        label: t`Operations`,
        panelIDs: [
          'user',
          'barcode-history',
          'background',
          'errors',
          'currencies',
          'email'
        ]
      },
      {
        id: 'data',
        label: t`Data Management`,
        panelIDs: [
          'import',
          'export',
          'project-codes',
          'custom-states',
          'custom-units'
        ]
      },
      {
        id: 'reporting',
        label: t`Reporting`,
        panelIDs: ['labels', 'reports', 'snippets', 'assets']
      },
      {
        id: 'plm',
        label: t`PLM`,
        panelIDs: [
          'selection-lists',
          'parameters',
          'category-parameters',
          'location-types',
          'stocktake'
        ]
      },
      {
        id: 'extend',
        label: t`Extend / Integrate`,
        panelIDs: ['plugin', 'machine']
      }
    ];
  }, []);

  return (
    <>
      <PageTitle title={t`Admin Center`} />
      {user.isStaff() ? (
        <Stack gap='xs'>
          <SettingsHeader
            label='admin'
            title={t`Admin Center`}
            subtitle={t`Advanced Options`}
          />
          <PanelGroup
            pageKey='admin-center'
            panels={adminCenterPanels}
            groups={grouping}
            collapsible={true}
            pluginPanelWithoutId
            pluginPanelKey={PluginPanelKey.admincenter}
          />
        </Stack>
      ) : (
        <PermissionDenied />
      )}
    </>
  );
}
