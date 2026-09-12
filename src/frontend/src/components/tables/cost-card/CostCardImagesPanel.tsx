import { t } from "@lingui/core/macro";
import {
  Badge,
  Box,
  Button,
  Group,
  LoadingOverlay,
  Paper,
  SimpleGrid,
  Text,
  FileButton,
  Tooltip,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconPhotoPlus, IconTrash, IconUpload } from "@tabler/icons-react";
import { useState } from "react";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import { ApiImage } from "@components/shared/images/ApiImage";
import { useApi } from "@context/ApiContext";

import * as classes from "./CostCardImagesPanel.css";

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
    <SimpleGrid cols={{ base: 1, xs: 2, md: 3 }} spacing="lg" maw={900}>
      {SLOTS.map(({ field, label }) => {
        const src = instance?.[field];
        const busy = uploading === field;

        return (
          <Paper
            key={field}
            withBorder
            radius="md"
            className={classes.card}
            pos="relative"
          >
            <LoadingOverlay
              visible={busy}
              zIndex={2}
              overlayProps={{ radius: "md", blur: 1 }}
            />

            <Box className={classes.preview}>
              {src ? (
                <>
                  <Box className={classes.imageWrap}>
                    <ApiImage
                      src={src}
                      aria-label={label()}
                      fit="contain"
                      radius="sm"
                      className={classes.previewImage}
                    />
                  </Box>
                  <Box className={classes.overlay}>
                    <FileButton
                      onChange={(file) => file && patchImage(field, file)}
                      accept="image/*"
                    >
                      {(props) => (
                        <Button
                          {...props}
                          size="xs"
                          variant="white"
                          leftSection={<IconUpload size={14} />}
                          aria-label={t`Upload image`}
                        >
                          {t`Replace`}
                        </Button>
                      )}
                    </FileButton>
                    <Tooltip label={t`Remove image`} withinPortal>
                      <Button
                        size="xs"
                        color="red"
                        variant="filled"
                        onClick={() => patchImage(field, "")}
                        aria-label={t`Remove image`}
                      >
                        <IconTrash size={14} />
                      </Button>
                    </Tooltip>
                  </Box>
                </>
              ) : (
                <FileButton
                  onChange={(file) => file && patchImage(field, file)}
                  accept="image/*"
                >
                  {(props) => (
                    <Box
                      {...props}
                      component="button"
                      type="button"
                      className={classes.empty}
                      aria-label={t`Upload image`}
                    >
                      <IconPhotoPlus size={28} stroke={1.5} />
                      <Text component="span" size="xs" fw={500}>
                        {t`Upload image`}
                      </Text>
                      <Text component="span" size="xs" c="dimmed">
                        {t`PNG or JPG`}
                      </Text>
                    </Box>
                  )}
                </FileButton>
              )}
            </Box>

            <Group
              className={classes.footer}
              justify="space-between"
              wrap="nowrap"
              px="sm"
              py="xs"
            >
              <Text size="sm" fw={500}>
                {label()}
              </Text>
              <Badge
                size="sm"
                radius="sm"
                variant="light"
                color={src ? "green" : "gray"}
              >
                {src ? t`Uploaded` : t`Empty`}
              </Badge>
            </Group>
          </Paper>
        );
      })}
    </SimpleGrid>
  );
}
