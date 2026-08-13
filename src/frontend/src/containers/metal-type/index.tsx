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
    ];
  }, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Metal Types`} />
      <PanelGroup pageKey="metal-type-index" panels={panels} />
    </Stack>
  );
}
