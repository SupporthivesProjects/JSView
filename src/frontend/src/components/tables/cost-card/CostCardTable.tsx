import { t } from "@lingui/core/macro";
import { useCallback, useEffect, useMemo, useState } from "react";

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
import { costCardFields, stampFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";
import { Thumbnail } from "@components/shared/images/Thumbnail";
import { Button, Group } from "@mantine/core";
import { useApi } from "@context/ApiContext";
import { useQuery, useQueryClient } from "@tanstack/react-query";

const COST_CARD_LOOKUP_QUERY_KEYS = [
  ["cost-card-customer-lookup"],
  ["cost-card-jewel-category-lookup"],
  ["cost-card-jewel-sub-category-lookup"],
];

export default function CostCardTable() {
  const table = useTable("cost-card");
  const user = useUserState();
  const api = useApi();
  const queryClient = useQueryClient();

  const refreshLookupTables = useCallback(() => {
    COST_CARD_LOOKUP_QUERY_KEYS.forEach((queryKey) => {
      queryClient.invalidateQueries({ queryKey });
    });
  }, [queryClient]);

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

  // --- Create modal ----------------------------------------------------

  const [createPreviewImage, setCreatePreviewImage] = useState<
    string | undefined
  >(undefined);

  const handleCreateImageChange = useCallback((file: File | null) => {
    setCreatePreviewImage((prev) => {
      if (prev) URL.revokeObjectURL(prev); // free the old blob url
      return file ? URL.createObjectURL(file) : undefined;
    });
  }, []);
  const newStamp = useCreateApiFormModal({
    url: ApiEndpoints.cost_card,
    title: t`Add Stamp`,
    fields: costCardFields(true, handleCreateImageChange), // allow to create image hence true
    table: table,
    preFormContent: (
      <Group justify="center" mb="sm">
        <Thumbnail src={createPreviewImage} alt={t`New Stamp`} size={60} />
      </Group>
    ),
    onClose: () => {
      setCreatePreviewImage((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return undefined;
      });
    },
    onFormSuccess: () => {
      refreshLookupTables();
    },
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedStamp, setSelectedStamp] = useState<any | undefined>(
    undefined,
  );
  const [changeImage, setChangeImage] = useState(false);
  const [previewImage, setPreviewImage] = useState<string | undefined>(
    undefined,
  );

  const handleImageChange = useCallback((file: File | null) => {
    setPreviewImage((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return file ? URL.createObjectURL(file) : undefined;
    });
  }, []);

  const editStamp = useEditApiFormModal({
    url: ApiEndpoints.cost_card,
    pk: selectedStamp?.pk,
    title: t`Edit Stamp`,
    fields: costCardFields(changeImage, handleImageChange),
    table: table,
    preFormContent: (
      <Group justify="space-between" mb="sm">
        <Thumbnail
          src={previewImage ?? selectedStamp?.image}
          alt={selectedStamp?.name}
          size={60}
        />
        {!changeImage && (
          <Button
            variant="subtle"
            size="xs"
            onClick={() => setChangeImage(true)}
          >
            {t`Change Image`}
          </Button>
        )}
      </Group>
    ),
    onClose: () => {
      setChangeImage(false);
      setPreviewImage((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return undefined;
      });
    },
    onFormSuccess: () => {
      refreshLookupTables();
    },
  });

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
            setChangeImage(false);
            setPreviewImage(undefined);
            setSelectedStamp(record);
            editStamp.open();
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
    [user],
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
        onClick={() => newStamp.open()}
        tooltip={t`Add Stamp`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newStamp.modal}
      {editStamp.modal}
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
        }}
      />
    </>
  );
}
