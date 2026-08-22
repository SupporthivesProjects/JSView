import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { AddItemButton } from "@lib/components/AddItemButton";
import {
  type RowAction,
  RowAddContactAction,
  RowContactAction,
  RowDeleteAction,
  RowEditAction,
} from "@lib/components/RowActions";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import useTable from "@lib/hooks/UseTable";
import type { TableFilter } from "@lib/index";
import type { TableColumn } from "@lib/types/Tables";
import {
  BooleanColumn,
  DecimalColumn,
  DescriptionColumn,
} from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { customerContactFields, masterCustomer } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useApi } from "@context/ApiContext";
import { useUserState } from "@store/UserState";
import { useModal } from "../../../hooks/UseModal";
import { ContactsPanel } from "./sharedComponents/ContactsPanel";

export default function MasterCustomerTable() {
  const table = useTable("master-customer");

  const user = useUserState();
  const api = useApi();
  const queryClient = useQueryClient();
  const [selectedCustomer, setSelectedCustomer] = useState<number | undefined>(
    undefined,
  );

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "code",
        title: t`Code`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "name",
        title: t`Name`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "description",
        title: t`Description`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "website",
        title: t`Website`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "phone",
        title: t`Phone`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "email",
        title: t`Email`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "contact",
        title: t`Contact`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "link",
        title: t`Link`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "tax_id",
        title: t`Tax ID`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "fax",
        title: t`Fax`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "city",
        title: t`City`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "state",
        title: t`State`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "country",
        title: t`Country`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "rating",
        title: t`Rating`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "credit_limit",
        title: t`Credit Limit`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "ref_by",
        title: t`Referred By`,
        sortable: true,
        switchable: true,
      },
    ];
  }, []);

  // --- Create modal ----------------------------------------------------
  const newMasterCustomer = useCreateApiFormModal({
    url: ApiEndpoints.master_vendor_customer,
    title: t`Add Master Customer`,
    fields: masterCustomer(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------

  const editMasterCustomer = useEditApiFormModal({
    url: ApiEndpoints.master_vendor_customer,
    pk: selectedCustomer,
    title: t`Edit Master Customer`,
    fields: masterCustomer(),
    table: table,
  });

  const deleteMasterCustomer = useDeleteApiFormModal({
    url: ApiEndpoints.master_vendor_customer,
    pk: selectedCustomer,
    title: t`Delete Master Customer`,
    table: table,
  });

  // --- Contact modal ----------------------------------------------------
  const contactMasterCustomer = useModal({
    id: "master-customer-contacts",
    title: t`Customer Contacts`,
    size: "lg",
    children: (
      <ContactsPanel id={selectedCustomer} queryKey="customer-contact" />
    ),
  });
  const addContactMasterCustomer = useCreateApiFormModal({
    url: ApiEndpoints.master_vendor_customer_contact,
    title: t`Add Customer Contact `,
    fields: customerContactFields(),
    initialData: { company: selectedCustomer },
    table: table,
    onFormSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["customer-contact", selectedCustomer],
      });
    },
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowContactAction({
          hidden: !user.hasViewRole(UserRoles.part),
          onClick: () => {
            setSelectedCustomer(record.pk);
            contactMasterCustomer.open();
          },
        }),
        RowAddContactAction({
          hidden: !user.hasAddRole(UserRoles.part),
          onClick: () => {
            setSelectedCustomer(record.pk);
            addContactMasterCustomer.open();
          },
        }),
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedCustomer(record.pk);
            editMasterCustomer.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedCustomer(record.pk);
            deleteMasterCustomer.open();
          },
        }),
      ];
    },
    [
      user,
    ],
  );

  // --- Table-level filters ----------------------------------------------
  const tableFilters: TableFilter[] = useMemo(() => {
    return [
      {
        name: "active",
        label: t`Active`,
        description: t`Show active master customer`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-master-customer"
        onClick={() => newMasterCustomer.open()}
        tooltip={t`Add Master Customer`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newMasterCustomer.modal}
      {editMasterCustomer.modal}
      {deleteMasterCustomer.modal}
      {contactMasterCustomer.modal}
      {addContactMasterCustomer.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.master_vendor_customer)}
        tableState={table}
        columns={columns}
        props={{
          rowActions: rowActions,
          tableActions: tableActions,
          tableFilters: tableFilters,
          enableDownload: true,
          params: { is_customer: true },
          dataFormatter: (data: any[]) =>
            (data ?? []).filter((row) => row.is_customer === true),
        }}
      />
    </>
  );
}
