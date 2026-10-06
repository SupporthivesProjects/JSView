import { t } from "@lingui/core/macro";
import { Stack } from "@mantine/core";
import { useMemo } from "react";

import {
  IconFileInvoice,
  IconFileInvoiceFilled,
  IconPhoto,
  IconDiamond,
  IconClipboardCheck,
  IconClipboardList,
  IconScale,
  IconReceipt,
} from "@tabler/icons-react";

import { UserRoles } from "@lib/enums/Roles";
import type { PanelType } from "@lib/types/Panel";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import { PanelGroup } from "@components/shared/panels/PanelGroup";
import { useUserState } from "@store/UserState";
import VendorShipmentTable from "@components/tables/vendor-shipment/VendorShipmentTable";
import ConfirmShipmentPanel from "@components/tables/vendor-shipment/ConfirmShipmentPanel";
import OpenOrderReport from "@components/tables/reports/OpenOrderReport";
import CloseOrderReport from "@components/tables/reports/CloseOrderReport";
import InvoiceValueReport from "@components/tables/reports/InvoiceValueReport";
import POStoneValuationReport from "@components/tables/reports/POStoneValuationReport";
import POStatusReport from "@components/tables/reports/POStatusReport";

export default function ReportsIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
    return [
      {
        name: "open-order",
        label: t`Open Order`,
        icon: <IconClipboardList />,
        content: <OpenOrderReport />,
      },
      {
        name: "close-order",
        label: t`Close Order`,
        icon: <IconClipboardCheck />,
        content: <CloseOrderReport />,
      },
      {
        name: "invoice-value",
        label: t`Invoice Value P/C`,
        icon: <IconFileInvoice />,
        content: <InvoiceValueReport />,
      },
      {
        name: "picture-presentation",
        label: t`Picture Presentation`,
        icon: <IconPhoto />,
        content: "",
      },
      {
        name: "po-stone-valuation",
        label: t`P.O. Stone Valuation`,
        icon: <IconDiamond />,
        content: <POStoneValuationReport />,
      },
      {
        name: "po-stone-status",
        label: t`P.O. Stone Status`,
        icon: <IconDiamond />,
        content: "",
      },
      {
        name: "po-status",
        label: t`P.O. Status`,
        icon: <IconClipboardList />,
        content: <POStatusReport />,
      },
      {
        name: "balance-vendor",
        label: t`Balance Dia. With Vendor`,
        icon: <IconScale />,
        content: "",
      },
      {
        name: "cost-card-export",
        label: t`Cost Card Export`,
        icon: <IconReceipt />,
        content: "",
      },
    ];
  }, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Reports`} />
      <PanelGroup pageKey="reports-index" panels={panels} fillHeight />
    </Stack>
  );
}
