import './App.css'
import ClerkProviderWithRoutes from './auth/ClerkProviderWithRoutes.jsx'
import {Routes, Route} from "react-router-dom"
import Layout from './layout/Layout.jsx'
import ChallengeGenerator from './challenge/ChallengeGenerator.jsx'
import HistoryPanel from './history/HistoryPanel.jsx'
import Authentication from './auth/Authentication.jsx'

function App() {

  return (
    <ClerkProviderWithRoutes>
       <Routes>
           <Route path='/sign-in/*' element={<Authentication/>}/>
           <Route path='/sign-up' element={<Authentication/>}/>
           <Route element={<Layout/>}>
               <Route path='/' element={<ChallengeGenerator/>}/>
               <Route path='/history' element={<HistoryPanel/>}/>
           </Route>

       </Routes>
    </ClerkProviderWithRoutes>
  )
}

export default App
