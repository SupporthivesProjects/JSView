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
import { jewellerySubCategoryFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

export default function JewellerySubCategoryTable() {
  const table = useTable("jewellery-sub-category");
  const user = useUserState();

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "category",
        sortable: true,
        switchable: false,
      },
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
  const newJewellerySubCategory = useCreateApiFormModal({
    url: ApiEndpoints.jewellery_sub_category,
    title: t`Add Jewel Sub Category`,
    fields: jewellerySubCategoryFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedJewellerySubCategory, setSelectedJewellerySubCategory] =
    useState<number | undefined>(undefined);

  const editJewellerySubCategory = useEditApiFormModal({
    url: ApiEndpoints.jewellery_sub_category,
    pk: selectedJewellerySubCategory,
    title: t`Edit Jewel Sub Category`,
    fields: jewellerySubCategoryFields(),
    table: table,
  });

  const deleteJewellerySubCategory = useDeleteApiFormModal({
    url: ApiEndpoints.jewellery_sub_category,
    pk: selectedJewellerySubCategory,
    title: t`Delete Jewel Sub Category`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedJewellerySubCategory(record.pk);
            editJewellerySubCategory.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedJewellerySubCategory(record.pk);
            deleteJewellerySubCategory.open();
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
        description: t`Show active jewellery sub category`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-jewellery-sub-category"
        onClick={() => newJewellerySubCategory.open()}
        tooltip={t`Add Jewellery Sub Category`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newJewellerySubCategory.modal}
      {editJewellerySubCategory.modal}
      {deleteJewellerySubCategory.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.jewellery_sub_category)}
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
