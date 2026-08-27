import { UnstyledButton } from "@mantine/core";

import { InvenTreeLogo } from "../ui/items/InvenTreeLogo";

export function NavHoverMenu({
  openDrawer,
}: Readonly<{
  openDrawer: () => void;
}>) {
  return (
    <UnstyledButton onClick={() => openDrawer()} aria-label="navigation-menu">
      {/* <InvenTreeLogo /> */}
      <img
        src="https://jsiview.com/assets/logo-CfMhCKIT.png"
        alt="jsiviewlogo"
        height={28}
      />
    </UnstyledButton>
  );
}
