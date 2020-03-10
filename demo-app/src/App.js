import React from 'react';
import './App.css';
import io from 'socket.io-client';
import Plot from 'react-plotly.js';
import TrafficLight from 'react-trafficlight';
import Incident_Table from './Table';



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
	    <div>
		<IDS_Plot ref={this.idsPlot}/>
		<div id="container"> </div>
	    </div>
	);
    };

    componentDidMount(){
	document.body.style.backgroundColor = '#ACB2B9'
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
const IDS_THRESHOLD = 0.5
var  IS_TRAINING = true

export class IDS_Plot extends React.PureComponent{

    constructor(props){
	super(props)
	this.state = {
	    calls_per_second : {
		y: [],
		x: [],
		name: ""
	    },
	    ids_score: {
		y: [],
		x: [],
		name: ""
	    },
	    original_data:{
		x: [],
		y: [],
		ids_score: []
	    },
	    training: 'Training ongoing',
	    alarm: 1,
	    index: 0
	}
	this.trafficLight = React.createRef();
	this.incidentTable = React.createRef();
    this.thresholdSlider = React.createRef();
    }


    // recieves data from App which implements websocket
    // calculate window for plotly fill
    updatePlot = (data) => {
	//console.log([data['calls_per_second'], data['time_of_first_call_minute']])
	let y = this.state.original_data.y
	let x = this.state.original_data.x
	let ids_score = this.state.original_data.ids_score
	// insert sent data into data object of plot
	if (data['ids_score'] != null) {
	    IS_TRAINING = false
	    ids_score.push(data['ids_score'])
	    var ids_state = "Detecting"
	}
	else if (IS_TRAINING){
	    var ids_state = "Training ongoing"
	    ids_score.push(0)
	}
	else {
	    ids_score.push(0)
	    var ids_state = "Detecting"
	}
	y.push(data['calls_per_second'])
	x.push(this.state.index)
	// only show static window of PLOT_WINDOW_CUTOUT seconds
	var cutout_ids = this.state.ids_score.cutout_ids
	var cutout_y = this.state.calls_per_second.cutout_y
	var cutout_x = this.state.calls_per_second.cutout_x
	// select only last entries of original data for cutout window
	cutout_ids = ids_score.slice(Math.max(ids_score.length - PLOT_WINDOW_CUTOUT, 1))
	cutout_x = x.slice(Math.max(x.length - PLOT_WINDOW_CUTOUT, 1))
	cutout_y = y.slice(Math.max(y.length - PLOT_WINDOW_CUTOUT, 1))

	// fill in zeros in y -> Entries with no record (because nothing was recorded) set to 0
	// fill in negative numbers so first value of y starts at x = 0
	if (cutout_x.length < PLOT_WINDOW_CUTOUT){
	    var new_cutout_x = new Array(PLOT_WINDOW_CUTOUT - cutout_x.length).fill(0)
	    for(var i = PLOT_WINDOW_CUTOUT - cutout_x.length; i > 0; i--){
		new_cutout_x[i-1] = -(i-1)
	    }
	    var new_cutout_y = new Array(PLOT_WINDOW_CUTOUT - cutout_y.length).fill(0)
	    var new_cutout_ids = new Array(PLOT_WINDOW_CUTOUT - cutout_ids.length).fill(0)
	    cutout_ids = new_cutout_ids.concat(cutout_ids)
	    cutout_x = new_cutout_x.concat(cutout_x)
	    cutout_y = new_cutout_y.concat(cutout_y)
	}

	//when alarm triggered
	// update table with incidents
	// update traffic light
	var current_score = ids_score[ids_score.length - 1]
	if(current_score > IDS_THRESHOLD){
	    var lights = [true,false,false]
	    console.log(this.state.index)
	    this.incidentTable.current.updateTable(this.state.index, current_score)
	}
	else {
	    var lights = [false,false,true]
	    console.log(this.state.index)
	}
	this.trafficLight.current.updateLight(lights)

	this.setState({
	    calls_per_second : {
            x: cutout_x,
            y: cutout_y,
            name: 'Time series data'
	    },
	    ids_score: {
            x: cutout_x,
            y: cutout_ids,
            name: 'IDS score data',
	    },
	    original_data:{
            x: x,
            y: y,
            ids_score: ids_score
	    },
	    ids_state: ids_state,
	    index: this.state.index + 1
	});
    }

    render(){
	return(
	    <div>
		<div> {this.state.ids_state} </div>
		<Plot
		    data={[
			{
			    x: this.state.calls_per_second.x,
			    y: this.state.calls_per_second.y,
			    mode: 'markers',
			    type: 'scatter'
			}
		    ]}
		    layout = {
			{
			    title : "Systemcalls in container",
			    xaxis : {
				title : "Seconds"
			    },
			    yaxis : {
				title : "Amount of Systemcalls"
			    },
			    datarevision : this.state.index,
			    paper_bgcolor: 'rgba(0,0,0,0)',
			    plot_bgcolor: 'rgba(0,0,0,0)'

			}
		    }
		/>
		<Plot
		    data={[
			{
			    x: this.state.ids_score.x,
			    y: this.state.ids_score.y,
			    mode: 'markers',
			    type: 'scatter'
			}
		    ]}
		    layout = {
			{
			    title : "IDS-Score",
			    xaxis : {
				title : "Seconds"
			    },
			    yaxis : {
				title : "Highest Score In Last Second"
			    },
			    datarevision : this.state.index,
			    paper_bgcolor: 'rgba(0,0,0,0)',
			    plot_bgcolor: 'rgba(0,0,0,0)',
                shapes: [
                    {
                        type: 'line',
                        xref: 'paper',
                        y0: IDS_THRESHOLD,
                        y1: IDS_THRESHOLD,
                        x0: this.state.ids_score.x[0],
                        x1: this.state.calls_per_second.x[this.state.calls_per_second.x.length - 1],
                        line:{
                            color: 'rgb(255,0,10)',
                            width: 2
                        }
                    }
                ]
			}
		    }

		/>
		<TrafficLightContainer ref={this.trafficLight}/>
		<Incident_Table ref={this.incidentTable}/>
	    </div>
	)
    }
    componentDidMount(){
    }
}

export class TrafficLightContainer extends React.PureComponent {
    state = {
	redOn: true,
	yellowOn: false,
	greenOn: false,
    }

    updateLight = (state) => {
	this.setState({
	    redOn: state[0],
	    yellowOn: state[1],
	    greenOn: state[2]
	});
    }

    render() {
	return (
	<TrafficLight
	    RedOn={this.state.redOn}
	    YellowOn={this.state.yellowOn}
	    GreenOn={this.state.greenOn}
	/>
	);
    }
}

