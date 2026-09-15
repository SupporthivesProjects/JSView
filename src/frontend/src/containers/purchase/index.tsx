import { t } from "@lingui/core/macro";
import { Stack } from "@mantine/core";
import { IconAtom2, IconIdBadge } from "@tabler/icons-react";
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
import PurchaseRequestTable from "@components/tables/purchase/purchase-request";
import PurchaseOrderTable from "@components/tables/purchase/purchase-order";

export default function MetalTypeIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
    return [
      {
        name: "purchase-request",
        label: t`Purchase Request`,
        icon: <IconCoin />,
        content: <PurchaseRequestTable />,
      },
      {
        name: "purchase-order",
        label: t`Purchase Order`,
        icon: <IconScale />,
        content: <PurchaseOrderTable />,
      },
      
    ];
  }, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Purchase`} />
      <PanelGroup pageKey="purchase-request-index" panels={panels} fillHeight />
    </Stack>
  );
}
