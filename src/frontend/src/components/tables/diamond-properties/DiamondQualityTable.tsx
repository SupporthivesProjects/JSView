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
import { diamondQualityFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

export default function DiamondQualityTable() {
  const table = useTable("diamond-quality");
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
  const newDiamondQuality = useCreateApiFormModal({
    url: ApiEndpoints.diamond_quality_list,
    title: t`Add Diamond Quality`,
    fields: diamondQualityFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedDiamondQuality, setSelectedDiamondQuality] = useState<
    number | undefined
  >(undefined);

  const editDiamondQuality = useEditApiFormModal({
    url: ApiEndpoints.diamond_quality_list,
    pk: selectedDiamondQuality,
    title: t`Edit Diamond Quality`,
    fields: diamondQualityFields(),
    table: table,
  });

  const deleteDiamondQuality = useDeleteApiFormModal({
    url: ApiEndpoints.diamond_quality_list,
    pk: selectedDiamondQuality,
    title: t`Delete Diamond Quality`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondQuality(record.pk);
            editDiamondQuality.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondQuality(record.pk);
            deleteDiamondQuality.open();
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
        description: t`Show active diamond quality`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-diamond-quality"
        onClick={() => newDiamondQuality.open()}
        tooltip={t`Add Diamond Quality`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newDiamondQuality.modal}
      {editDiamondQuality.modal}
      {deleteDiamondQuality.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.diamond_quality_list)}
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
