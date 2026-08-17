import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

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
import { BooleanColumn, DecimalColumn, DescriptionColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { masterTerms } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useApi } from "@context/ApiContext";
import { useUserState } from "@store/UserState";

/**
 * Table for displaying, creating, editing and deleting Metal Purity records
 */
export default function MasterTermsTable() {
  const table = useTable("master-terms");

  const user = useUserState();
  const api = useApi();

  // The list endpoint only returns the related MetalType's primary key
  // (no nested "metal_type_detail" is provided by the backend serializer,
  // and we're not changing the backend to add one) - so fetch the small
  // list of metal types once ourselves and build a pk -> name lookup for
  // the column below, instead of showing a bare numeric id.
//   const masterTermsQuery = useQuery({
//     queryKey: ["master-terms-lookup"],
//     queryFn: () =>
//       api
//         .get(apiUrl(ApiEndpoints.metal_type_list), { params: { limit: 1000 } })
//         .then((response) => response.data?.results ?? response.data ?? []),
//     staleTime: 5 * 60 * 1000,
//   });

  // Active-only subset for the create/edit form's Metal Type dropdown -
  // the backend doesn't filter this itself, so it's done here in JS.
//   const activeMetalTypes = useMemo(() => {
//     return (metalTypesQuery.data ?? []).filter(
//       (metalType: any) => metalType.active,
//     );
//   }, [metalTypesQuery.data]);

//   const metalTypeNameByPk = useMemo(() => {
//     const map: Record<number, string> = {};
//     (metalTypesQuery.data ?? []).forEach((metalType: any) => {
//       map[metalType.pk] = metalType.name;
//     });
//     return map;
//   }, [metalTypesQuery.data]);

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "name",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "days",
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
  const newMasterTerms = useCreateApiFormModal({
    url: ApiEndpoints.master_terms,
    title: t`Add Master Terms`,
    fields: masterTerms(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedTerms, setSelectedTerms] = useState<
    number | undefined
  >(undefined);

  const editMasterTerms = useEditApiFormModal({
    url: ApiEndpoints.master_terms,
    pk: selectedTerms,
    title: t`Edit Master Terms`,
    fields: masterTerms(),
    table: table,
  });

  const deleteMasterTerms = useDeleteApiFormModal({
    url: ApiEndpoints.master_terms,
    pk: selectedTerms,
    title: t`Delete Master Terms`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedTerms(record.pk);
            editMasterTerms.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedTerms(record.pk);
            deleteMasterTerms.open();
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
        description: t`Show active master terms`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-master-terms"
        onClick={() => newMasterTerms.open()}
        tooltip={t`Add Master Terms`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newMasterTerms.modal}
      {editMasterTerms.modal}
      {deleteMasterTerms.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.master_terms)}
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
