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
import { diamondCutFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";
import { useQueryClient } from "@tanstack/react-query";

export default function DiamondCutTable() {
  const table = useTable("diamond-cut");
  const user = useUserState();
  const queryClient = useQueryClient();

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
  const newDiamondCut = useCreateApiFormModal({
    url: ApiEndpoints.diamond_cut_list,
    title: t`Add Diamond Cut`,
    fields: diamondCutFields(),
    table: table,
    onFormSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["diamond-cut-lookup"] });
    },
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedDiamondCut, setSelectedDiamondCut] = useState<
    number | undefined
  >(undefined);

  const editDiamondCut = useEditApiFormModal({
    url: ApiEndpoints.diamond_cut_list,
    pk: selectedDiamondCut,
    title: t`Edit Diamond Cut`,
    fields: diamondCutFields(),
    table: table,
    onFormSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["diamond-cut-lookup"] });
    },
  });

  const deleteDiamondCut = useDeleteApiFormModal({
    url: ApiEndpoints.diamond_cut_list,
    pk: selectedDiamondCut,
    title: t`Delete Diamond Cut`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondCut(record.pk);
            editDiamondCut.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondCut(record.pk);
            deleteDiamondCut.open();
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
        description: t`Show active diamond cut`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-diamond-cut"
        onClick={() => newDiamondCut.open()}
        tooltip={t`Add Diamond Cut`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newDiamondCut.modal}
      {editDiamondCut.modal}
      {deleteDiamondCut.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.diamond_cut_list)}
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
