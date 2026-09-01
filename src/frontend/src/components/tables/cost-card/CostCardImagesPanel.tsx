import { t } from "@lingui/core/macro";
import { ActionIcon, FileButton, Group, Stack, Text } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconCirclePlus, IconCircleMinus } from "@tabler/icons-react";
import { useState } from "react";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import { Thumbnail } from "@components/shared/images/Thumbnail";
import { useApi } from "@context/ApiContext";

type ImageSlot = "front_view" | "side_view" | "back_view";

const SLOTS: { field: ImageSlot; label: () => string }[] = [
  { field: "front_view", label: () => t`Front View` },
  { field: "side_view", label: () => t`Side View` },
  { field: "back_view", label: () => t`Back View` },
];

/**
 * Images tab — front / side / back views of the piece, stored via the
 * dedicated cost-card-images upload endpoint (rather than the main cost
 * card PATCH), since they are uploaded as multipart form data.
 */
export default function CostCardImagesPanel({
  costCardId,
  instance,
  onUpdated,
}: Readonly<{
  costCardId: number;
  instance: any;
  onUpdated: (data: any) => void;
}>) {
  const api = useApi();
  const [uploading, setUploading] = useState<ImageSlot | undefined>(
    undefined,
  );

  const patchImage = (field: ImageSlot, value: File | "") => {
    setUploading(field);

    const formData = new FormData();
    formData.append(field, value);

    api
      .patch(apiUrl(ApiEndpoints.cost_card_images, costCardId), formData)
      .then((response) => {
        onUpdated(response.data);
      })
      .catch(() => {
        notifications.show({
          title: t`Error`,
          message: t`Failed to update image`,
          color: "red",
        });
      })
      .finally(() => {
        setUploading(undefined);
      });
  };

  return (
    <Group align="flex-start" gap="xl" wrap="wrap">
      {SLOTS.map(({ field, label }) => (
        <Stack key={field} gap="xs" align="center">
          <Text size="sm">{label()}</Text>
          <Thumbnail src={instance?.[field]} alt={label()} size={160} hover />
          <Group gap="xs">
            <FileButton
              onChange={(file) => file && patchImage(field, file)}
              accept="image/*"
            >
              {(props) => (
                <ActionIcon
                  {...props}
                  variant="subtle"
                  color="green"
                  loading={uploading === field}
                  aria-label={t`Upload image`}
                >
                  <IconCirclePlus />
                </ActionIcon>
              )}
            </FileButton>
            <ActionIcon
              variant="subtle"
              color="red"
              disabled={!instance?.[field]}
              loading={uploading === field}
              onClick={() => patchImage(field, "")}
              aria-label={t`Remove image`}
            >
              <IconCircleMinus />
            </ActionIcon>
          </Group>
        </Stack>
      ))}
    </Group>
  );
}
