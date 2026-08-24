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
import type { TableFilter } from "@lib/index";
import type { TableColumn } from "@lib/types/Tables";
import { BooleanColumn, DescriptionColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { DiamondStoneFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

export default function DiamondStoneTable() {
  const table = useTable("diamond-stone");
  const user = useUserState();

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "name",
        sortable: true,
        switchable: false,
      },
      DescriptionColumn({}),
      BooleanColumn({
        accessor: "active",
      }),
      {
        accessor: "created_at",
        title: t`Created`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "updated_at",
        title: t`Updated`,
        sortable: true,
        switchable: true,
      },
    ];
  }, []);

  // --- Create modal ----------------------------------------------------
  const newDiamondStone = useCreateApiFormModal({
    url: ApiEndpoints.diamond_stone_list,
    title: t`Add Diamond Stone`,
    fields: DiamondStoneFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedDiamondStone, setSelectedDiamondStone] = useState<
    number | undefined
  >(undefined);

  const editDiamondStone = useEditApiFormModal({
    url: ApiEndpoints.diamond_stone_list,
    pk: selectedDiamondStone,
    title: t`Edit Diamond Stome`,
    fields: DiamondStoneFields(),
    table: table,
  });

  const deleteDiamondStone = useDeleteApiFormModal({
    url: ApiEndpoints.diamond_stone_list,
    pk: selectedDiamondStone,
    title: t`Delete Diamond Stone`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondStone(record.pk);
            editDiamondStone.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondStone(record.pk);
            deleteDiamondStone.open();
          },
        }),
      ];
    },
    [user],
  );

  // --- Table-level filters ----------------------------------------------
  const tableFilters: TableFilter[] = useMemo(() => {
    return [
      {
        name: "active",
        label: t`Active`,
        description: t`Show active Diamond Stone`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-diamond-stone"
        onClick={() => newDiamondStone.open()}
        tooltip={t`Add Diamond Stone`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newDiamondStone.modal}
      {editDiamondStone.modal}
      {deleteDiamondStone.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.diamond_stone_list)}
        tableState={table}
        columns={columns}
        props={{
          rowActions: rowActions,
          tableActions: tableActions,
          tableFilters: tableFilters,
          enableDownload: true,
        }}
      />
    </>
  );
}
