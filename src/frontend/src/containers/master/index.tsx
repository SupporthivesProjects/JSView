import { t } from "@lingui/core/macro";
import { Stack } from "@mantine/core";
import { IconAtom2 } from "@tabler/icons-react";
import { useMemo } from "react";

import { UserRoles } from "@lib/enums/Roles";
import type { PanelType } from "@lib/types/Panel";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import { PanelGroup } from "@components/shared/panels/PanelGroup";
import { useUserState } from "@store/UserState";
import MetalTypeTable from "@components/tables/metal/MetalTypeTable";
import MetalPurityTable from "@components/tables/metal/MetalPurityTable";
import MetalRateTable from "@components/tables/metal/MetalRateTable";
import FindingTypeTable from "@components/tables/metal/FindingTypeTable";
import FinishTypeTable from "@components/tables/metal/FinishTypeTable";
import ListDutyTable from "@components/tables/metal/ListDutyTable";
import MasterTermsTable from "@components/tables/metal/MasterTermsTable";
import MasterExecutiveTable from "@components/tables/metal/MasterExecutiveTable";
import CourierServiceTable from "@components/tables/metal/CourierServiceTable";
import MasterSettingsTable from "@components/tables/metal/MasterSettingsTable";
import LabourSettingTable from "@components/tables/metal/LabourSettingsTable";

export default function MetalTypeIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
    return [
      {
        name: "metal-types",
        label: t`Metal Types`,
        icon: <IconAtom2 />,
        content: <MetalTypeTable />,
      },
      {
        name: "metal-purity",
        label: t`Metal Purity`,
        icon: <IconAtom2 />,
        content: <MetalPurityTable />,
      },
      {
        name: "metal-rate",
        label: t`Metal Rate`,
        icon: <IconAtom2 />,
        content: <MetalRateTable />,
      },
      {
        name: "finding-type",
        label: t`Finding Type`,
        icon: <IconAtom2 />,
        content: <FindingTypeTable />,
      },
      {
        name: "finish-type",
        label: t`Finish Type`,
        icon: <IconAtom2 />,
        content: <FinishTypeTable />,
      },
      {
        name: "duty-list",
        label: t`Duty`,
        icon: <IconAtom2 />,
        content: <ListDutyTable />,
      },
      {
        name: "master-terms",
        label: t`Terms`,
        icon: <IconAtom2 />,
        content: <MasterTermsTable />,
      },
      {
        name: "master-executive",
        label: t`A/C Executive`,
        icon: <IconAtom2 />,
        content: <MasterExecutiveTable />,
      },
      {
        name: "courier-service",
        label: t`Courier Service`,
        icon: <IconAtom2 />,
        content: <CourierServiceTable />,
      },
      {
        name: "settings",
        label: t`Settings`,
        icon: <IconAtom2 />,
        content: <MasterSettingsTable />,
      },
      {
        name: "labour-setting",
        label: t`Labour Settings`,
        icon: <IconAtom2 />,
        content: <LabourSettingTable />,
      },
    ];
  }, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Master`} />
      <PanelGroup pageKey="metal-type-index" panels={panels} />
    </Stack>
  );
}
