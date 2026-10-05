import { t } from "@lingui/core/macro";
import {
  Button,
  Group,
  Paper,
  Stack,
  Text,
  ThemeIcon,
  Title,
} from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { notifications } from "@mantine/notifications";
import { IconDiamond, IconFileSpreadsheet } from "@tabler/icons-react";
import dayjs from "dayjs";
import { useState } from "react";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import { useApi } from "@context/ApiContext";
import useDataOutput from "../../../hooks/UseDataOutput";

const DATE_FORMAT = "YYYY-MM-DD";

export default function POStoneValuationReport() {
  const api = useApi();
  const [loading, setLoading] = useState(false);
  const [exportId, setExportId] = useState<number | undefined>(undefined);

  // Defaults to the start of the year up to today
  const [dateFrom, setDateFrom] = useState<string | null>(
    dayjs().startOf("year").format(DATE_FORMAT),
  );
  const [dateTo, setDateTo] = useState<string | null>(
    dayjs().format(DATE_FORMAT),
  );

  const invalidRange =
    !!dateFrom && !!dateTo && dayjs(dateFrom).isAfter(dayjs(dateTo));

  useDataOutput({
    title: t`Exporting P.O. Stone Valuation Report`,
    id: exportId,
  });

  /* The export builds the workbook server side and returns a DataOutput
   * record, which is then monitored until the file can be downloaded.
   */
  const downloadReport = () => {
    if (!dateFrom || !dateTo || invalidRange) return;

    setLoading(true);
    api
      .get(apiUrl(ApiEndpoints.reports_po_stone_valuation), {
        params: {
          date_from: dayjs(dateFrom).format(DATE_FORMAT),
          date_to: dayjs(dateTo).format(DATE_FORMAT),
          export: true,
          export_format: "xlsx",
        },
      })
      .then((response) => setExportId(response.data?.pk))
      .catch(() => {
        notifications.show({
          title: t`Export failed`,
          message: t`Could not export the P.O. stone valuation report`,
          color: "red",
        });
      })
      .finally(() => setLoading(false));
  };

  return (
    <Stack gap="md">
      <Stack gap={2}>
        <Title order={4}>{t`P.O. Stone Valuation Report`}</Title>
        <Text size="sm" c="dimmed">
          {t`Export P.O. stone valuation for a date range as an Excel workbook`}
        </Text>
      </Stack>

      <Paper withBorder radius="md" p="lg" shadow="xs" maw={640}>
        <Stack gap="md">
          <Group gap="sm">
            <ThemeIcon size={42} radius="md" variant="light" color="blue">
              <IconDiamond size={22} />
            </ThemeIcon>
            <Stack gap={0}>
              <Text fw={600}>{t`Date Range`}</Text>
              <Text size="sm" c="dimmed">
                {t`P.O.s dated within the selected range`}
              </Text>
            </Stack>
          </Group>

          <Group grow align="flex-start">
            <DateInput
              label={t`From`}
              value={dateFrom}
              onChange={setDateFrom}
              valueFormat="DD MMM YYYY"
              maxDate={dateTo ?? undefined}
              required
            />
            <DateInput
              label={t`To`}
              value={dateTo}
              onChange={setDateTo}
              valueFormat="DD MMM YYYY"
              minDate={dateFrom ?? undefined}
              error={invalidRange ? t`Must be after the From date` : undefined}
              required
            />
          </Group>

          <Button
            fullWidth
            radius="md"
            leftSection={<IconFileSpreadsheet size={18} />}
            loading={loading}
            disabled={!dateFrom || !dateTo || invalidRange}
            onClick={downloadReport}
          >
            {t`Download Excel`}
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}
