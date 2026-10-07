import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useRef } from "react";

import { type RowAction, RowEditAction } from "@lib/components/RowActions";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import useTable from "@lib/hooks/UseTable";
import type { TableColumn } from "@lib/types/Tables";
import { useApi } from "@context/ApiContext";
import { showApiErrorMessage } from "@helpers/notifications";
import { useColumnFilters } from "../ColumnFilters";
import { InvenTreeTable } from "../InvenTreeTable";
import usePicturePresentation from "../cost-card/usePicturePresentation";

/*
 * Picture presentations are not stored on their own: each purchase order is
 * listed as one, and editing it opens the cost card Presentation form with
 * that order and the cost cards on its lines already filled in.
 */
export default function PicturePresentationReport() {
  const table = useTable("picture-presentation-report");
  const api = useApi();

  // Per-column search boxes, applied together (multi-level / AND filtering)
  const { activeColumnFilters, columnFilter, clearColumnFiltersAction } =
    useColumnFilters(table);

  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "pono",
        title: t`Picture Presentation No.`,
        sortable: false,
        switchable: false,
        ...columnFilter("pono_search", t`Picture Presentation No.`),
      },
      {
        accessor: "customer_name",
        title: t`Name`,
        sortable: false,
        switchable: false,
        ...columnFilter("customer_search", t`Name`),
      },
    ];
  }, [columnFilter]);

  const presentation = usePicturePresentation();

  // Guards against a second click while the cost cards are being loaded
  const opening = useRef<boolean>(false);

  // The form lists each card's stone lines and pre-fills the pricing inputs
  // from the cards, so they are fetched before it opens
  const openPresentation = useCallback(
    async (po: any) => {
      if (opening.current) {
        return;
      }

      const cardPks: number[] = Array.from(
        new Set(
          (po.lines ?? [])
            .map((line: any) => line?.costcardid)
            .filter((pk: any) => !!pk)
            .map((pk: any) => Number(pk)),
        ),
      );

      opening.current = true;

      try {
        const records = await Promise.all(
          cardPks.map((pk) =>
            api
              .get(apiUrl(ApiEndpoints.cost_card, pk))
              .then((response) => response.data)
              .catch(() => null),
          ),
        );

        presentation.open({
          records: records.filter((record) => !!record),
          po: po.pk,
        });
      } catch (error: any) {
        showApiErrorMessage({ error: error, title: t`Picture Presentation` });
      } finally {
        opening.current = false;
      }
    },
    [api, presentation.open],
  );

  const rowActions = useCallback(
    (record: any): RowAction[] => [
      RowEditAction({
        onClick: () => openPresentation(record),
      }),
    ],
    [openPresentation],
  );

  const tableActions = useMemo(
    () => [clearColumnFiltersAction],
    [clearColumnFiltersAction],
  );

  return (
    <>
      {presentation.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.purchase_api)}
        tableState={table}
        columns={columns}
        props={{
          params: {
            potype: "ORDER",
            active: true,
            ...activeColumnFilters,
          },
          rowActions: rowActions,
          tableActions: tableActions,
        }}
      />
    </>
  );
}
