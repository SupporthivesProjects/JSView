import { t } from "@lingui/core/macro";
import { Stack, Tabs } from "@mantine/core";
import { IconDiamond, IconPalette } from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";

import { UserRoles } from "@lib/enums/Roles";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import { PanelGroup } from "@components/shared/panels/PanelGroup";
import { useUserState } from "@store/UserState";
import { useColorStonePropertyPanels } from "./ColorStonePropertiesPanels";
import { useDiamondPropertyPanels } from "./DiamondPropertiesPanels";

/* The two property sets shown on this page. Each one is a top level tab,
 * and maps onto the first path segment below /properties/
 */
export type PropertySection = "diamond" | "color-stone";

export default function PropertiesIndex({
  section,
}: Readonly<{ section: PropertySection }>) {
  const user = useUserState();
  const navigate = useNavigate();

  const diamondPanels = useDiamondPropertyPanels();
  const colorStonePanels = useColorStonePropertyPanels();

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  const isDiamond = section === "diamond";

  return (
    <Stack>
      <PageDetail title={t`Properties`} />
      <Tabs
        value={section}
        onChange={(value) => value && navigate(`/properties/${value}/`)}
      >
        <Tabs.List>
          <Tabs.Tab value="diamond" leftSection={<IconDiamond size={16} />}>
            {t`Diamond Properties`}
          </Tabs.Tab>
          <Tabs.Tab value="color-stone" leftSection={<IconPalette size={16} />}>
            {t`Color Stone Properties`}
          </Tabs.Tab>
        </Tabs.List>
      </Tabs>
      <PanelGroup
        key={section}
        pageKey={isDiamond ? "diamond-stone-index" : "color-stone-index"}
        panels={isDiamond ? diamondPanels : colorStonePanels}
      />
    </Stack>
  );
}
