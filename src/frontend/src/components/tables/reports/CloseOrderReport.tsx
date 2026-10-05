import { t } from "@lingui/core/macro";
import {
  Button,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  ThemeIcon,
  Title,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
  IconBuildingStore,
  IconFileSpreadsheet,
  IconListDetails,
  IconUsers,
} from "@tabler/icons-react";
import { type ReactNode, useState } from "react";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import { useApi } from "@context/ApiContext";
import useDataOutput from "../../../hooks/UseDataOutput";

type ReportType = "all" | "vendor" | "customer";

type ReportOption = {
  type: ReportType;
  title: string;
  description: string;
  icon: ReactNode;
  color: string;
};

export default function CloseOrderReport() {
  const api = useApi();
  const [loading, setLoading] = useState<ReportType | null>(null);
  const [exportId, setExportId] = useState<number | undefined>(undefined);
  const [exportTitle, setExportTitle] = useState<string>("");

  useDataOutput({
    title:
      t`Exporting Close Order Report` + (exportTitle ? ` (${exportTitle})` : ""),
    id: exportId,
  });

  const options: ReportOption[] = [
    {
      type: "all",
      title: t`All Vendors`,
      description: t`Close orders across every vendor in a single sheet`,
      icon: <IconListDetails size={22} />,
      color: "blue",
    },
    {
      type: "vendor",
      title: t`Vendor Wise`,
      description: t`Close orders grouped by vendor`,
      icon: <IconBuildingStore size={22} />,
      color: "teal",
    },
    {
      type: "customer",
      title: t`Customer Wise`,
      description: t`Close orders grouped by customer`,
      icon: <IconUsers size={22} />,
      color: "violet",
    },
  ];

  /* The export builds the workbook server side and returns a DataOutput
   * record, which is then monitored until the file can be downloaded.
   */
  const downloadReport = (type: ReportType) => {
    setLoading(type);
    api
      .get(apiUrl(ApiEndpoints.reports_close_order), {
        params: {
          report_type: type,
          export: true,
          export_format: "xlsx",
        },
      })
      .then((response) => {
        setExportTitle(
          options.find((option) => option.type === type)?.title ?? "",
        );
        setExportId(response.data?.pk);
      })
      .catch(() => {
        notifications.show({
          title: t`Export failed`,
          message: t`Could not export the close order report`,
          color: "red",
        });
      })
      .finally(() => setLoading(null));
  };

  return (
    <Stack gap="md">
      <Stack gap={2}>
        <Title order={4}>{t`Close Order Reports`}</Title>
        <Text size="sm" c="dimmed">
          {t`Export close orders as an Excel workbook`}
        </Text>
      </Stack>

      <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="md">
        {options.map((option) => (
          <Paper key={option.type} withBorder radius="md" p="lg" shadow="xs">
            <Stack gap="md" h="100%" justify="space-between">
              <Stack gap="xs">
                <ThemeIcon
                  size={42}
                  radius="md"
                  variant="light"
                  color={option.color}
                >
                  {option.icon}
                </ThemeIcon>
                <Text fw={600}>{option.title}</Text>
                <Text size="sm" c="dimmed">
                  {option.description}
                </Text>
              </Stack>

              <Button
                fullWidth
                radius="md"
                color={option.color}
                leftSection={<IconFileSpreadsheet size={18} />}
                loading={loading === option.type}
                disabled={loading !== null && loading !== option.type}
                onClick={() => downloadReport(option.type)}
              >
                {t`Download Excel`}
              </Button>
            </Stack>
          </Paper>
        ))}
      </SimpleGrid>
    </Stack>
  );
}
