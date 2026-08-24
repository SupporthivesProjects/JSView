import { lazy } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { EagerLoadable, Loadable } from "@helpers/loading";
import { onLocaleReady } from "@helpers/localeReady";

// Lazy loaded pages
// These two are mutually exclusive and one of them is always needed
// immediately on initial load, so they're loaded eagerly rather than via
// Loadable/lazy - see EagerLoadable for why.
export const LayoutComponent = EagerLoadable(
  () => import("@components/layouts/AppLayout"),
);
export const LoginLayoutComponent = EagerLoadable(
  () => import("@components/layouts/AuthLayout"),
);

export const Home = Loadable(lazy(() => import("@containers/home")));

export const CompanyDetail = Loadable(
  lazy(() => import("@containers/company")),
);

export const CustomerDetail = Loadable(
  lazy(() => import("@containers/customer")),
);

export const SupplierDetail = Loadable(
  lazy(() => import("@containers/supplier")),
);

export const ManufacturerDetail = Loadable(
  lazy(() => import("@containers/manufacturer")),
);

export const SupplierPartDetail = Loadable(
  lazy(() => import("@containers/supplier-part")),
);

export const ManufacturerPartDetail = Loadable(
  lazy(() => import("@containers/manufacturer-part")),
);

export const CategoryDetail = Loadable(
  lazy(() => import("@containers/part-category")),
);
export const PartDetail = Loadable(
  lazy(() => import("@containers/part-detail")),
);

export const MasterIndex = Loadable(lazy(() => import("@containers/master")));

export const DiamondPropertiesIndex = Loadable(
  lazy(() => import("@containers/diamond-properties")),
);

export const LocationDetail = Loadable(
  lazy(() => import("@containers/stock-location")),
);

export const StockDetail = Loadable(
  lazy(() => import("@containers/stock-item")),
);

export const BuildIndex = Loadable(
  lazy(() => import("@containers/manufacturing")),
);

export const BuildDetail = Loadable(
  lazy(() => import("@containers/build-order")),
);

export const PurchasingIndex = Loadable(
  lazy(() => import("@containers/purchasing")),
);

export const PurchaseOrderDetail = Loadable(
  lazy(() => import("@containers/purchase-order")),
);

export const SalesIndex = Loadable(lazy(() => import("@containers/sales")));

export const SalesOrderDetail = Loadable(
  lazy(() => import("@containers/sales-order")),
);

export const SalesOrderShipmentDetail = Loadable(
  lazy(() => import("@containers/sales-order-shipment")),
);

export const ReturnOrderDetail = Loadable(
  lazy(() => import("@containers/return-order")),
);

export const TransferOrderDetail = Loadable(
  lazy(() => import("@containers/stock-transfer-order")),
);

export const Scan = Loadable(lazy(() => import("@containers/scan")));

export const ErrorPage = Loadable(
  lazy(() => import("@components/shared/errors/ErrorPage")),
);

export const Notifications = Loadable(
  lazy(() => import("@containers/notifications")),
);

export const UserSettings = Loadable(
  lazy(() => import("@containers/settings-user")),
);

export const SystemSettings = Loadable(
  lazy(() => import("@containers/settings-system")),
);

export const AdminCenter = Loadable(
  lazy(() => import("@containers/settings-admin")),
);

// Core object
export const CoreIndex = Loadable(lazy(() => import("@containers/core")));
export const UserDetail = Loadable(lazy(() => import("@containers/core-user")));
export const GroupDetail = Loadable(
  lazy(() => import("@containers/core-group")),
);

export const NotFound = Loadable(lazy(() => import("@containers/not-found")));

// Auth
export const Login = Loadable(lazy(() => import("@containers/login")));
// LoggedIn is the auth-check gateway hit by every fresh, unauthenticated
// page load (redirected to from ProtectedRoute) - load it eagerly too.
export const LoggedIn = EagerLoadable(() => import("@containers/logged-in"));

// These three are all needed within the first render pass or two of any
// fresh page load, so start fetching them as soon as it's safe to (i.e. as
// soon as the active locale is set) rather than waiting for each to mount
// in turn - mounting only happens after the previous one in the chain has
// already rendered and redirected, so waiting for mount compounds several
// round trips of otherwise-avoidable latency.
onLocaleReady(() => {
  LayoutComponent.preload();
  LoginLayoutComponent.preload();
  LoggedIn.preload();
});
export const Logout = Loadable(lazy(() => import("@containers/logout")));
export const Register = Loadable(lazy(() => import("@containers/register")));
export const Mfa = Loadable(lazy(() => import("@containers/mfa")));
export const MfaSetup = Loadable(lazy(() => import("@containers/mfa-setup")));
export const ChangePassword = Loadable(
  lazy(() => import("@containers/change-password")),
);
export const Reset = Loadable(lazy(() => import("@containers/reset-password")));
export const ResetPassword = Loadable(
  lazy(() => import("@containers/set-password")),
);
export const VerifyEmail = Loadable(
  lazy(() => import("@containers/verify-email")),
  true,
  true,
);

// Routes
export const routes = (
  <Routes>
    <Route path="*" element={<NotFound />} errorElement={<ErrorPage />} />
    <Route path="/" element={<LayoutComponent />} errorElement={<ErrorPage />}>
      <Route index element={<Home />} />,
      <Route path="home/" element={<Home />} />,
      <Route path="notifications/*" element={<Notifications />} />,
      <Route path="scan/" element={<Scan />} />,
      <Route path="settings/">
        <Route index element={<Navigate to="admin/" />} />
        <Route path="admin/*" element={<AdminCenter />} />
        <Route path="system/*" element={<SystemSettings />} />
        <Route path="user/*" element={<UserSettings />} />
      </Route>
      <Route path="part/">
        <Route index element={<Navigate to="category/index/" />} />
        <Route path="category/:id?/*" element={<CategoryDetail />} />
        <Route path=":id/*" element={<PartDetail />} />
      </Route>
      <Route path="diamond-properties/">
        <Route index element={<Navigate to="metal-types/" />} />
        <Route path="*" element={<DiamondPropertiesIndex />} />
      </Route>
      <Route path="master/">
        <Route index element={<Navigate to="metal-types/" />} />
        <Route path="*" element={<MasterIndex />} />
      </Route>
      <Route path="stock/">
        <Route index element={<Navigate to="location/index/" />} />
        <Route path="location/:id?/*" element={<LocationDetail />} />
        <Route path="item/:id/*" element={<StockDetail />} />
        <Route path="transfer-order/:id/*" element={<TransferOrderDetail />} />
      </Route>
      <Route path="manufacturing/">
        <Route index element={<Navigate to="index/" />} />
        <Route path="index/*" element={<BuildIndex />} />
        <Route path="build-order/:id/*" element={<BuildDetail />} />
      </Route>
      <Route path="purchasing/">
        <Route index element={<Navigate to="index/" />} />
        <Route path="index/*" element={<PurchasingIndex />} />
        <Route path="purchase-order/:id/*" element={<PurchaseOrderDetail />} />
        <Route path="supplier/:id/*" element={<SupplierDetail />} />
        <Route path="supplier-part/:id/*" element={<SupplierPartDetail />} />
        <Route path="manufacturer/:id/*" element={<ManufacturerDetail />} />
        <Route
          path="manufacturer-part/:id/*"
          element={<ManufacturerPartDetail />}
        />
      </Route>
      <Route path="company/:id/*" element={<CompanyDetail />} />
      <Route path="sales/">
        <Route index element={<Navigate to="index/" />} />
        <Route path="index/*" element={<SalesIndex />} />
        <Route path="sales-order/:id/*" element={<SalesOrderDetail />} />
        <Route path="shipment/:id/*" element={<SalesOrderShipmentDetail />} />
        <Route path="return-order/:id/*" element={<ReturnOrderDetail />} />
        <Route path="customer/:id/*" element={<CustomerDetail />} />
      </Route>
      <Route path="core/">
        <Route index element={<Navigate to="index/" />} />
        <Route path="index/*" element={<CoreIndex />} />
        <Route path="user/:id/*" element={<UserDetail />} />
        <Route path="group/:id/*" element={<GroupDetail />} />
      </Route>
    </Route>
    <Route
      path="/"
      element={<LoginLayoutComponent />}
      errorElement={<ErrorPage />}
    >
      <Route path="/login" element={<Login />} />,
      <Route path="/logged-in" element={<LoggedIn />} />
      <Route path="/logout" element={<Logout />} />,
      <Route path="/register" element={<Register />} />,
      <Route path="/mfa" element={<Mfa />} />,
      <Route path="/mfa-setup" element={<MfaSetup />} />,
      <Route path="/change-password" element={<ChangePassword />} />
      <Route path="/reset-password" element={<Reset />} />
      <Route path="/set-password" element={<ResetPassword />} />
      <Route path="/verify-email/:key" element={<VerifyEmail />} />
    </Route>
  </Routes>
);
