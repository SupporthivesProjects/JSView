import { t } from "@lingui/core/macro";
import { Stack } from "@mantine/core";
import { IconAtom2 } from "@tabler/icons-react";
import { useMemo } from "react";

import {
  IconBrush,
  IconBuildingStore,
  IconCertificate,
  IconCoin,
  IconComponents,
  IconDiamond,
  IconFileDescription,
  IconHammer,
  IconReceiptTax,
  IconScale,
  IconSettings,
  IconTag,
  IconTrendingUp,
  IconTruckDelivery,
  IconUserCheck,
  IconUsers,
} from "@tabler/icons-react";

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
import MasterVendorTable from "@components/tables/metal/MasterVendorTable";
import MasterCustomerTable from "@components/tables/metal/MasterCustomerTable";
import JewelleryCategoryTable from "@components/tables/metal/JewelleryCategoryTable";
import JewellerySubCategoryTable from "@components/tables/metal/JewellerySubCategoryTable";
import StampTable from "@components/tables/metal/StampTable";
import DiamondStoneTable from "@components/tables/diamond-properties/diamondStoneTable";
import DiamondCutTable from "@components/tables/diamond-properties/DiamondCutTable";
import DiamondShapeTable from "@components/tables/diamond-properties/DiamondShapeTable";
import DiamondColorTable from "@components/tables/diamond-properties/DiamondColorTable";

export default function DiamondPropertiesIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
    return [
      {
        name: "diamond-stone",
        label: t`Diamond Stone`,
        icon: <IconCoin />,
        content: <DiamondStoneTable />,
      },
      {
        name: "diamond-cut",
        label: t`Diamond Cut`,
        icon: <IconCoin />,
        content: <DiamondCutTable />,
      },
      {
        name: "diamond-shape",
        label: t`Diamond Shape`,
        icon: <IconCoin />,
        content: <DiamondShapeTable />,
      },
      {
        name: "diamond-color",
        label: t`Diamond Color`,
        icon: <IconCoin />,
        content: <DiamondColorTable />,
      },
    ];
  }, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Diamond Stone`} />
      <PanelGroup pageKey="diamond-stone-index" panels={panels} />
    </Stack>
  );
}
