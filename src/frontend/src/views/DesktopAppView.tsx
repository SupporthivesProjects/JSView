import { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';

import { getBaseUrl } from '@lib/functions/Navigation';
import { useShallow } from 'zustand/react/shallow';
import { api, queryClient } from '@app-lib/api/client';
import { ApiProvider } from '@context/ApiContext';
import { ThemeContext } from '@context/ThemeContext';
import { defaultHostList } from '@config/defaultHostList';
import { routes } from '@routes/router';
import { useLocalState } from '@store/LocalState';

export default function DesktopAppView() {
  const [hostList] = useLocalState(useShallow((state) => [state.hostList]));

  useEffect(() => {
    if (Object.keys(hostList).length === 0) {
      useLocalState.setState({ hostList: defaultHostList });
    }
  }, [hostList]);

  return (
    <ApiProvider client={queryClient} api={api}>
      <ThemeContext>
        <BrowserRouter basename={getBaseUrl()}>{routes}</BrowserRouter>
      </ThemeContext>
    </ApiProvider>
  );
}
