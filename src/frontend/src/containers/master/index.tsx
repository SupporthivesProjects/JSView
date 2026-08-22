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

export default function MetalTypeIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
    return [
      {
        name: "metal-types",
        label: t`Metal Types`,
        icon: <IconCoin />,
        content: <MetalTypeTable />,
      },
      {
        name: "metal-purity",
        label: t`Metal Purity`,
        icon: <IconScale />,
        content: <MetalPurityTable />,
      },
      {
        name: "jewellery-category",
        label: t`Jewel Category`,
        icon: <IconDiamond />,
        content: <JewelleryCategoryTable />,
      },
      {
        name: "jewellery-sub-category",
        label: t`Jewel Sub Category`,
        icon: <IconTag />,
        content: <JewellerySubCategoryTable />,
      },
      {
        name: "settings",
        label: t`Settings`,
        icon: <IconSettings />,
        content: <MasterSettingsTable />,
      },
      {
        name: "labour-setting",
        label: t`Labour Settings`,
        icon: <IconHammer />,
        content: <LabourSettingTable />,
      },
      {
        name: "metal-rate",
        label: t`Metal Rate`,
        icon: <IconTrendingUp />,
        content: <MetalRateTable />,
      },
      {
        name: "finding-type",
        label: t`Finding Type`,
        icon: <IconComponents />,
        content: <FindingTypeTable />,
      },
      {
        name: "master-customer",
        label: t`Customer`,
        icon: <IconUsers />,
        content: <MasterCustomerTable />,
      },
      {
        name: "master-vendor",
        label: t`Vendor`,
        icon: <IconBuildingStore />,
        content: <MasterVendorTable />,
      },
      {
        name: "finish-type",
        label: t`Finish Type`,
        icon: <IconBrush />,
        content: <FinishTypeTable />,
      },
      {
        name: "duty-list",
        label: t`Duty`,
        icon: <IconReceiptTax />,
        content: <ListDutyTable />,
      },
      {
        name: "stamp",
        label: t`Stamp`,
        icon: <IconCertificate />,
        content: <StampTable />,
      },
      {
        name: "master-executive",
        label: t`A/C Executive`,
        icon: <IconUserCheck />,
        content: <MasterExecutiveTable />,
      },
      {
        name: "master-terms",
        label: t`Terms`,
        icon: <IconFileDescription />,
        content: <MasterTermsTable />,
      },
      {
        name: "courier-service",
        label: t`Courier Service`,
        icon: <IconTruckDelivery />,
        content: <CourierServiceTable />,
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
