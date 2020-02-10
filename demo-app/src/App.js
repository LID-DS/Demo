import React from 'react';
import './App.css';
import { w3cwebsocket as W3CWebSocket } from "websocket";

const URL = 'ws://127.0.0.1:5000'

class App extends React.PureComponent{
    constructor(props){
	super(props)
	this.state = {
	    sum : 0
	}
	this.client = new W3CWebSocket(URL)
    }

    render(){
	return(
	    <div>{this.state.sum}</div>
	)
    }
    componentDidMount(){
	this.client.onopen = () => this.client.send("read")
    }
}


export default App;
