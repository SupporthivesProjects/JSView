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
import { jewelleryCategoryFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

export default function JewelleryCategoryTable() {
  const table = useTable("jewellery-category");
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
  const newJewelleryCategory = useCreateApiFormModal({
    url: ApiEndpoints.jewellery_category,
    title: t`Add Jewel Category`,
    fields: jewelleryCategoryFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedJewelleryCategory, setSelectedJewelleryCategory] = useState<
    number | undefined
  >(undefined);

  const editJewelleryCategory = useEditApiFormModal({
    url: ApiEndpoints.jewellery_category,
    pk: selectedJewelleryCategory,
    title: t`Edit Jewel Category`,
    fields: jewelleryCategoryFields(),
    table: table,
  });

  const deleteJewelleryCategory = useDeleteApiFormModal({
    url: ApiEndpoints.jewellery_category,
    pk: selectedJewelleryCategory,
    title: t`Delete Jewel Category`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedJewelleryCategory(record.pk);
            editJewelleryCategory.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedJewelleryCategory(record.pk);
            deleteJewelleryCategory.open();
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
        description: t`Show active jewellery category`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-jewellery-category"
        onClick={() => newJewelleryCategory.open()}
        tooltip={t`Add Jewellery Category`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newJewelleryCategory.modal}
      {editJewelleryCategory.modal}
      {deleteJewelleryCategory.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.jewellery_category)}
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
