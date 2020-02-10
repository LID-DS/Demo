import React from 'react';
import './App.css';
import { w3cwebsocket as W3CWebSocket } from "websocket";


class App extends React.PureComponent{
    constructor(props){
		super(props)
		this.state = {
	    	sum : 0
		}
		this.client = new W3CWebSocket('ws://0.0.0.0:8015');
    }

    render(){
		return(
			<div>{this.state.sum}</div>
		)
    }
    componentDidMount(){
	}
}


export default App;
