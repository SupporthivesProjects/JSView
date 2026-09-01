import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useState } from "react";

import { AddItemButton } from "@lib/components/AddItemButton";
import {
  type RowAction,
  RowDeleteAction,
  RowEditAction,
} from "@lib/components/RowActions";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import useTable from "@lib/hooks/UseTable";
import type { TableColumn } from "@lib/types/Tables";
import { InvenTreeTable } from "../InvenTreeTable";
import { costCardFinishLineFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import useNameLookup from "../../../hooks/UseNameLookup";
import { useUserState } from "@store/UserState";

/**
 * Finish Type tab — one row per finish applied to a cost card.
 */
export default function CostCardFinishLineTable({
  costCardId,
}: Readonly<{ costCardId: number }>) {
  const table = useTable("cost-card-finish-line");
  const user = useUserState();

  const { nameByPk: finishTypeByPk } = useNameLookup(
    ApiEndpoints.finish_type,
    "cost-card-finish-type-lookup",
  );

  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "finish_type",
        title: t`Finish Type`,
        sortable: false,
        switchable: false,
        render: (record: any) =>
          finishTypeByPk[record.finish_type] ?? record.finish_type,
      },
      {
        accessor: "rate",
        title: t`Price`,
        sortable: true,
        switchable: false,
      },
    ];
  }, [finishTypeByPk]);

  // --- Create modal ----------------------------------------------------
  const newLine = useCreateApiFormModal({
    url: ApiEndpoints.cost_card_finish_line,
    title: t`Add Finish Type`,
    fields: costCardFinishLineFields(costCardId),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedLine, setSelectedLine] = useState<number | undefined>(
    undefined,
  );

  const editLine = useEditApiFormModal({
    url: ApiEndpoints.cost_card_finish_line,
    pk: selectedLine,
    title: t`Edit Finish Type`,
    fields: costCardFinishLineFields(costCardId),
    table: table,
  });

  const deleteLine = useDeleteApiFormModal({
    url: ApiEndpoints.cost_card_finish_line,
    pk: selectedLine,
    title: t`Delete Finish Type`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedLine(record.pk);
            editLine.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedLine(record.pk);
            deleteLine.open();
          },
        }),
      ];
    },
    [user],
  );

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-finish-line"
        onClick={() => newLine.open()}
        tooltip={t`Add Finish Type`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newLine.modal}
      {editLine.modal}
      {deleteLine.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.cost_card_finish_line)}
        tableState={table}
        columns={columns}
        props={{
          params: { cost_card: costCardId },
          rowActions: rowActions,
          tableActions: tableActions,
        }}
      />
    </>
  );
}
