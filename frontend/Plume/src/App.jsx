import { useAuth } from './AuthContext';
import Authpage from './components/authpage';
import Daily from './components/daily';

export default function App()
{
    const   { userId } = useAuth();

    return userId ? <Daily/> : <Authpage/>;
}