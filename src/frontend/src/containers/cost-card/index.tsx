import { t } from "@lingui/core/macro";
import { Stack } from "@mantine/core";
import { IconAtom2 } from "@tabler/icons-react";
import { useMemo } from "react";

import {
  IconCoin,
  IconScale,
} from "@tabler/icons-react";

import { UserRoles } from "@lib/enums/Roles";
import type { PanelType } from "@lib/types/Panel";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import { PanelGroup } from "@components/shared/panels/PanelGroup";
import { useUserState } from "@store/UserState";
import MetalPurityTable from "@components/tables/metal/MetalPurityTable";
import CostCardTable from "@components/tables/cost-card/CostCardTable";

export default function CostCardIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
    return [
      {
        name: "cost-card",
        label: t`Cost Card`,
        icon: <IconCoin />,
        content: <CostCardTable />,
      },
    //   {
    //     name: "style-card",
    //     label: t`Style Card`,
    //     icon: <IconScale />,
    //     content: <MetalPurityTable />,
    //   },
    ];
  }, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Cost Card`} />
      <PanelGroup pageKey="cost-card-index" panels={panels} />
    </Stack>
  );
}
