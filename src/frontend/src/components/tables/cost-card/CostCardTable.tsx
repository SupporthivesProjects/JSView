import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

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
import { BooleanColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { useDeleteApiFormModal } from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";
import { Thumbnail } from "@components/shared/images/Thumbnail";
import { Group } from "@mantine/core";
import { useApi } from "@context/ApiContext";
import { useQuery } from "@tanstack/react-query";

export default function CostCardTable() {
  const table = useTable("cost-card");
  const user = useUserState();
  const api = useApi();
  const navigate = useNavigate();

  // Customer / Vendor (both are Company records)
  const companyQuery = useQuery({
    queryKey: ["cost-card-customer-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.master_vendor_customer), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const customerNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (companyQuery.data ?? []).forEach((company: any) => {
      if (company.is_customer) {
        map[company.pk] = company.name;
      }
    });
    return map;
  }, [companyQuery.data]);

  const vendorNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (companyQuery.data ?? []).forEach((company: any) => {
      if (company.is_supplier) {
        map[company.pk] = company.name;
      }
    });
    return map;
  }, [companyQuery.data]);

  // Jewel Category
  const jewelCategoryQuery = useQuery({
    queryKey: ["cost-card-jewel-category-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.jewellery_category), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const jewelCategoryNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (jewelCategoryQuery.data ?? []).forEach((category: any) => {
      map[category.pk] = category.name;
    });
    return map;
  }, [jewelCategoryQuery.data]);

  // Jewel Sub Category
  const jewelSubCategoryQuery = useQuery({
    queryKey: ["cost-card-jewel-sub-category-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.jewellery_sub_category), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const jewelSubCategoryNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (jewelSubCategoryQuery.data ?? []).forEach((subCategory: any) => {
      map[subCategory.pk] = subCategory.name;
    });
    return map;
  }, [jewelSubCategoryQuery.data]);

  // --- new Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "image",
        title: t`Image`,
        sortable: false,
        switchable: true,
        render: (record: any) => (
          <Group gap="xs" wrap="nowrap">
            <Thumbnail
              src={record.front_view}
              alt={t`Front View`}
              size={24}
              hover
            />
            <Thumbnail
              src={record.back_view}
              alt={t`Back View`}
              size={24}
              hover
            />
            <Thumbnail
              src={record.side_view}
              alt={t`Side View`}
              size={24}
              hover
            />
          </Group>
        ),
      },
      {
        accessor: "cost_card_no",
        title: t`Cost Card Number`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "our_style_no",
        title: t`Our Style Number`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "vendor_style_no",
        title: t`Vendor Style Number`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "customer",
        title: t`Customer`,
        sortable: true,
        switchable: false,
        render: (record: any) =>
          customerNameByPk[record.customer] ?? record.customer,
      },
      {
        accessor: "vendor",
        title: t`Vendor`,
        sortable: true,
        switchable: false,
        render: (record: any) =>
          vendorNameByPk[record.vendor] ?? record.vendor,
      },
      {
        accessor: "category",
        title: t`Jewel Category`,
        sortable: true,
        switchable: false,
        render: (record: any) =>
          jewelCategoryNameByPk[record.category] ?? record.category,
      },
      {
        accessor: "sub_category",
        title: t`Sub Category`,
        sortable: true,
        switchable: false,
        render: (record: any) =>
          jewelSubCategoryNameByPk[record.sub_category] ?? record.sub_category,
      },
      {
        accessor: "karat",
        title: t`Metal`,
        sortable: true,
        switchable: false,
      },
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
  }, [
    customerNameByPk,
    vendorNameByPk,
    jewelCategoryNameByPk,
    jewelSubCategoryNameByPk,
  ]);

  // --- Delete modal ------------------------------------------------------
  // Create and edit now happen on a dedicated tabbed page (see
  // containers/cost-card-detail) rather than in a modal, since a cost card
  // has line items (finish/diamond/color stone) and images that need their
  // own endpoints. Delete remains a modal since it's a single confirmation.
  const [selectedStamp, setSelectedStamp] = useState<number | undefined>(
    undefined,
  );

  const deleteStamp = useDeleteApiFormModal({
    url: ApiEndpoints.cost_card,
    pk: selectedStamp,
    title: t`Delete Stamp`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            navigate(`/cards/cost-card/${record.pk}`);
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedStamp(record.pk);
            deleteStamp.open();
          },
        }),
      ];
    },
    [user, navigate],
  );

  // --- Table-level filters ----------------------------------------------
  const tableFilters: TableFilter[] = useMemo(() => {
    return [
      {
        name: "active",
        label: t`Active`,
        description: t`Show active stamp`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-stamp"
        onClick={() => navigate("/cards/cost-card/new")}
        tooltip={t`Add Stamp`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user, navigate]);

  return (
    <>
      {deleteStamp.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.cost_card)}
        tableState={table}
        columns={columns}
        props={{
          rowActions: rowActions,
          tableActions: tableActions,
          tableFilters: tableFilters,
          enableDownload: true,
          onRowClick: (record: any) =>
            navigate(`/cards/cost-card/${record.pk}`),
        }}
      />
    </>
  );
}
