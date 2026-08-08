import { t } from '@lingui/core/macro';

import GenericErrorPage from '@components/shared/errors/GenericErrorPage';

export default function NotFound() {
  return (
    <GenericErrorPage
      title={t`Page Not Found`}
      message={t`This page does not exist`}
    />
  );
}
