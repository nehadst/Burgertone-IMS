import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './components/Dashboard';

const queryClient = new QueryClient();

const theme = createTheme({
    palette: {
        mode: 'light',
        background: {
            default: '#f5f5f5'
        }
    },
});

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <Dashboard />
            </ThemeProvider>
        </QueryClientProvider>
    );
}

export default App;