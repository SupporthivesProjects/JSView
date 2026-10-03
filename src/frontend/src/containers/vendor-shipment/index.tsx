import { t } from "@lingui/core/macro";
import { Stack } from "@mantine/core";
import { useMemo } from "react";

import { IconCoin, IconDiamond, IconScale, IconTag } from "@tabler/icons-react";

import { UserRoles } from "@lib/enums/Roles";
import type { PanelType } from "@lib/types/Panel";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import { PanelGroup } from "@components/shared/panels/PanelGroup";
import { useUserState } from "@store/UserState";
import VendorShipmentTable from "@components/tables/vendor-shipment/VendorShipmentTable";
import ConfirmShipmentPanel from "@components/tables/vendor-shipment/ConfirmShipmentPanel";

export default function VendorShipmentIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
    return [
      {
        name: "shipment",
        label: t`Shipment`,
        icon: <IconCoin />,
        content: <VendorShipmentTable />,
      },
      {
        name: "confirm-shipment",
        label: t`Confirm Shipment`,
        icon: <IconScale />,
        content: <ConfirmShipmentPanel />,
      },
    ];
  }, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Vendor Shipment`} />
      <PanelGroup pageKey="vendor-shipment-index" panels={panels} fillHeight />
    </Stack>
  );
}
