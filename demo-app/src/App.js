import React from 'react';
import './App.css';
import io from 'socket.io-client';

class App extends React.PureComponent{

    constructor(props){
	super(props)
	this.state = {
	    sum : 0
	}
	console.log('start websocket')
    }

    render(){
	return(
		<div>{this.state.sum}</div>
	)
    }
    componentDidMount(){
	
	var socket = io('ws://localhost:5000/');
	socket.on('connect', function() {
	    console.log('connected')
	    socket.emit('get stats', 'sum')
	    //socket.emit('my event', {
		//data : 'Connected'
	    //});
	});
	socket.on('my response', function(data) {
	    console.log("somethin");
	});
	socket.on('stats_sum', function(data) {
	    console.log(data)
	    this.setState({
		sum : data['call_per_minute']
	    })
	}.bind(this));

    }
    componentWillUnmount() {
	clearInterval(this.interval);
    }
}


export default App;
