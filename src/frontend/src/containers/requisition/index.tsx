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
import MetalPurityTable from "@components/tables/metal/MetalPurityTable";
import JewelleryCategoryTable from "@components/tables/metal/JewelleryCategoryTable";
import JewellerySubCategoryTable from "@components/tables/metal/JewellerySubCategoryTable";
import StoneRequisitionTable from "@components/tables/requisition/StoneRequisitionTable";

export default function RequisitionTypeIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
    return [
      {
        name: "stone",
        label: t`Stone`,
        icon: <IconCoin />,
        content: <StoneRequisitionTable />,
      },
      {
        name: "metal",
        label: t`Metal`,
        icon: <IconScale />,
        content: <MetalPurityTable />,
      },
      {
        name: "flute-metal",
        label: t`Flute Metal`,
        icon: <IconDiamond />,
        content: <JewelleryCategoryTable />,
      },
      {
        name: "metal-sent",
        label: t`Metal Sent`,
        icon: <IconTag />,
        content: <JewellerySubCategoryTable />,
      },
    ];
  }, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Requisition`} customsubtitle={t`stone`} />
      <PanelGroup pageKey="requisition-type-index" panels={panels} fillHeight />
    </Stack>
  );
}
