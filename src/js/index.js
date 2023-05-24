import React from 'react';
import Status from './Status';
import ReactDOM from 'react-dom/client';
import {
    Route,
    Routes,
    HashRouter
} from "react-router-dom";
import Sidebar from './Sidebar';
import StartupOptimizer from './StartupOptimizer';
window.React = React;

// const router = createHashRouter(
//     createRoutesFromElements(
//         <Route path="/" element={<TestEle />}>
//             <Route path="dashboard" element={<Layout />} />
//         </Route>
//     )
// );
// TODO: upgrade to react router 6.4+ -> use createHashRouter and createRoutesFromElements
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
<>
    <HashRouter>
        <div id="header">
            <div id="headerContent">
                XYLENT Antivirus⚡
                {/* TODO: Make this a custom window title frame */}
            </div>
        </div>
        <div id="page">
            <div id="sideBar">
                <Sidebar />
            </div>
            <Routes>
                <Route path='/' element={<Status />} />
                <Route path='/status' element={<Status />} />
                <Route path='/optimize' element={<StartupOptimizer />}></Route>
            </Routes>
        </div>
    </HashRouter>
</>);