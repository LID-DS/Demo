import React from 'react';
import './App.css';
import io from 'socket.io-client';
import Plot from 'react-plotly.js';
//import SystemCall_Plot from './IDS_Plot'

const element = <h1>Hello, world!</h1>;

class App extends React.PureComponent{
    
    constructor(props){
	super(props)
	this.state = {
	    websocket:0,
	    data:[]
	}
	this.idsPlot = React.createRef();
    };

    render() {
	return(
	    element,
	    <IDS_Plot ref={this.idsPlot}/>
	);
    };

    
    componentDidMount(){
	let socket = io('ws://localhost:5000/');
	socket.on('connect', function() {
	    console.log('connected')
	    this.setState({
		websocket: socket
	    });
	}.bind(this));

	//if recieved message stats update plot 
	socket.on('stats', function(data) {
	    this.setState({
		data : data
	    });
	    this.idsPlot.current.updatePlot(data)
	}.bind(this));
    }
}


export default App;

const PLOT_WINDOW_CUTOUT = 60

export class SystemCall_Plot extends React.PureComponent{
    
    constructor(props){
	super(props)
	this.state = {
	    calls_per_second : {
		y : [],
		x : [],
		name: ""}, 
	    original_data:{
		x: [],
		y: [] 
	    },
	    index : 0 
	}
    }

    updatePlot = (data) => {
	//console.log([data['calls_per_second'], data['time_of_first_call_minute']])
	let y = this.state.original_data.y
	let x = this.state.original_data.x
	// insert sent data into data object of plot
	y.push(parseInt(data['calls_per_second']))
	x.push(this.state.index)
	// only show static window of PLOT_WINDOW_CUTOUT seconds
	var cutout_y = this.state.calls_per_second.cutout_y 
	var cutout_x = this.state.calls_per_second.cutout_x
	// select only last entries of original data for cutout window 
	cutout_x = x.slice(Math.max(x.length - PLOT_WINDOW_CUTOUT, 1))
	cutout_y = y.slice(Math.max(y.length - PLOT_WINDOW_CUTOUT, 1))

	// fill in zeros in y
	// fill in negative numbers so first value of y starts at x = 0
	if (cutout_x.length < PLOT_WINDOW_CUTOUT){
	    var new_cutout_x = new Array(PLOT_WINDOW_CUTOUT - cutout_x.length).fill(0)  
	    for(var i = PLOT_WINDOW_CUTOUT - cutout_x.length; i > 0; i--){
		new_cutout_x[i-1] = -(i-1) 
	    }
	    var new_cutout_y = new Array(PLOT_WINDOW_CUTOUT - cutout_y.length).fill(0)
	    cutout_x = new_cutout_x.concat(cutout_x)
	    cutout_y = new_cutout_y.concat(cutout_y)
	}

	this.setState({
	    calls_per_second : { 
	    x: cutout_x,
	    y: cutout_y,
		name: 'Time series data'
	    },
	    original_data:{
		x: x,
		y: y
	    },
	    index: this.state.index + 1
	});
    }

    render(){
	return(
	    <Plot
		data={[this.state.calls_per_second]}
		layout = {
		    {
			title : "Systemcalls in container", 
			xaxis : {
			    title : "Seconds"
			},
			yaxis : {
			    title : "Amount of Systemcalls"
			},
			datarevision : this.state.index
		    }
		}
            />
	)
    }
    componentDidMount(){
    }
}


export class IDS_Plot extends React.PureComponent{
    
    constructor(props){
	super(props)
	this.state = {
	    calls_per_second : {
		y : [],
		x : [],
		name: ""}, 
	    original_data:{
		x: [],
		y: [] 
	    },
	    index : 0 
	}
    }

    updatePlot = (data) => {
	console.log(data)
	//console.log([data['calls_per_second'], data['time_of_first_call_minute']])
	let y = this.state.original_data.y
	let x = this.state.original_data.x
	// insert sent data into data object of plot
	y.push(data['ids_score'])
	x.push(this.state.index)
	// only show static window of PLOT_WINDOW_CUTOUT seconds
	var cutout_y = this.state.calls_per_second.cutout_y 
	var cutout_x = this.state.calls_per_second.cutout_x
	// select only last entries of original data for cutout window 
	cutout_x = x.slice(Math.max(x.length - PLOT_WINDOW_CUTOUT, 1))
	cutout_y = y.slice(Math.max(y.length - PLOT_WINDOW_CUTOUT, 1))

	// fill in zeros in y
	// fill in negative numbers so first value of y starts at x = 0
	if (cutout_x.length < PLOT_WINDOW_CUTOUT){
	    var new_cutout_x = new Array(PLOT_WINDOW_CUTOUT - cutout_x.length).fill(0)  
	    for(var i = PLOT_WINDOW_CUTOUT - cutout_x.length; i > 0; i--){
		new_cutout_x[i-1] = -(i-1) 
	    }
	    var new_cutout_y = new Array(PLOT_WINDOW_CUTOUT - cutout_y.length).fill(0)
	    cutout_x = new_cutout_x.concat(cutout_x)
	    cutout_y = new_cutout_y.concat(cutout_y)
	}

	this.setState({
	    calls_per_second : { 
	    x: cutout_x,
	    y: cutout_y,
		name: 'Time series data'
	    },
	    original_data:{
		x: x,
		y: y
	    },
	    index: this.state.index + 1
	});
    }

    render(){
	return(
	    <Plot
		data={[this.state.calls_per_second]}
		layout = {
		    {
			title : "IDS-Score", 
			xaxis : {
			    title : "Seconds"
			},
			yaxis : {
			    title : "Highest Score In Last Second"
			},
			datarevision : this.state.index
		    }
		}
            />
	)
    }
    componentDidMount(){
    }
}
