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
import ColorStoneTable from "@components/tables/colorStone/ColorStoneTable";
import ColorStoneCutTable from "@components/tables/colorStone/ColorStoneCutTable";

export default function ColorStonePropertiesIndex() {
  const user = useUserState();

 const panels: PanelType[] = useMemo(() => {
  return [
    {
      name: "stone-types",
      label: t`Stone`,
      icon: <IconDiamond />,
      content: <ColorStoneTable />,
    },
    {
      name: "stone-cut",
      label: t`Cut`,
      icon: <IconDiamond />,
      content: <ColorStoneCutTable />,

    },
    {
      name: "color-stone-shape",
      label: t`Shape`,
      icon: <IconDiamond />,
    //   content: <ColorStoneShapeTable />,
      content: <MetalTypeTable />,
    },
    {
      name: "color-stone-color",
      label: t`Color`,
      icon: <IconDiamond />,
      //   content: <ColorStoneColorTable />,
      content: <MetalTypeTable />,
    },
    {
      name: "color-stone-size",
      label: t`Size`,
      icon: <IconDiamond />,
      //   content: <ColorStoneSizeTable />,
      content: <MetalTypeTable />,
    },
    {
      name: "color-stone-quality",
      label: t`Quality`,
      icon: <IconDiamond />,
    //   content: <ColorStoneQualityTable />,
      content: <MetalTypeTable />,
    },
    {
      name: "color-stone-weight-rate",
      label: t`Weight / Rate Per Stone`,
      icon: <IconDiamond />,
    //   content: <ColorStoneWeightRateTable />,
      content: <MetalTypeTable />,
    },
  ];
}, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Color Stone Properties`} />
      <PanelGroup pageKey="color-stone-index" panels={panels} />
    </Stack>
  );
}
