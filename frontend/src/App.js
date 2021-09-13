import React from 'react';
import {
    Route,
    Switch,
    withRouter
} from "react-router-dom";
import NodePage from "./pages/NodePage";
import MasterPage from "./pages/MasterPage";

function App() {
    return (
        <Switch>
            <Route exact path='/' component={MasterPage} />
            <Route exact path='/node/:id' component={NodePage} />
        </Switch>
    );
}

export default withRouter(App);
