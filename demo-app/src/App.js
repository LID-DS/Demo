import React from 'react';
import io from 'socket.io-client';
import Slider from 'react-input-slider';
import './css/App.css';

import IDSPlot from './IDSPlot';
import TrainingInfo from './TrainingInfo';
import IncidentTable from './Table';
import UserInput from './UserInput'
import UserActionInput from './UserActionInput'
import TrafficLight from './TrafficLight';
import SyscallTypePlot from './SyscallTypePlot';

const IDS_THRESHOLD = 0.5
const PLOT_WINDOW_CUTOUT = 60

const highlight_color = '#f9f5d7'
const highlight1_color = '#470a0a'
const background_color = '#0e1217'

class App extends React.PureComponent{

    constructor(props){
        super(props)
        this.state = {
            websocket:0,
            data:[],
            syscall_plot:{
                plot_type: "syscall",
                calls_per_second : {
                    y: [],
                    x: [],
                    name: ''
                },
                index: 0
            },
            ids_plot: {
                plot_type: "ids",
                ids_score: {
                    x: [], 
                    y: [],
                    name: '',
                },
                index: 0,
                slider_threshold: IDS_THRESHOLD
            },
            original_data:{
                x: [],
                y: [],
                ids_score: [] 
            },
            slider: {
                threshold: IDS_THRESHOLD
            },
            alarm: 0,
            index: 0,
            syscall_type_dist: {
                complete: {} ,
                top5: {},
            }
        }

        this.syscallDistPlot = React.createRef();
        this.trafficLight = React.createRef();
        this.idsPlot = React.createRef();
        this.trainingInfo = React.createRef();
        this.incidentTable = React.createRef();
        this.userAction = React.createRef();
    };
   
    //receive incident from IDSPlot 
    incidentHandler = (incident) => {
        this.incidentTable.current.updateTable(incident.index, incident.score)
    }

    //revceive info from TrainingInfo 
    trainingChangeHandle = (retrain_info) => {
        this.sendToBackend(retrain_info) 
    }
    
    //send info via websocket to backend 
    sendToBackend = (data) => {
       this.state.websocket.emit('training update', data) 
    }
    
    updateSyscallDistribution = (data) => {
        let top5 = [];
        var i;
        for (i = 0; i < 5; i++){
            top5.push(data['syscall_type_dict']['sorted_syscalls'][i]);
        }
        this.syscallDistPlot.current.handleValues(top5)
    }

    /*
        prepare plot data
        calc moving window for syscall and ids plot
        show correct trafficlight
    */
    preparePlotData = (data) => {
        //console.log([data['calls_per_second'], data['time_of_first_call_minute']])
        let y = this.state.original_data.y
        let x = this.state.original_data.x
        let ids_score = this.state.original_data.ids_score
        // insert sent data into data object of plot
         // and further information into ids_info

        if (data['ids_info']['score'] != null) {
            ids_score.push(data['ids_info']['score'])
        }
        else{
            ids_score.push(0)
        }   
        y.push(data['calls_per_second'])
        x.push(this.state.index)
        // only show static window of PLOT_WINDOW_CUTOUT seconds
        var cutout_ids = this.state.ids_plot.ids_score.cutout_ids
        var cutout_y = this.state.syscall_plot.calls_per_second.cutout_y
        var cutout_x = this.state.syscall_plot.calls_per_second.cutout_x
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
        var lights = []
        var current_score = ids_score[ids_score.length - 1]
        //if still in training set light to yellow
        if(data['ids_info']['state'] === 0){
            lights = [false,true,false]
        }
        //when alarm triggered
        // update traffic light
        // set alarm state so App.js can access it
        else if(current_score > this.state.slider.threshold){
            lights = [true,false,false]
            this.setState({alarm: 1})
            //console.log(this.state.index)
        }
        else {
            lights = [false,false,true]
            this.setState({alarm: 0})
            //console.log(this.state.index)
        }
        this.trafficLight.current.updateLight(lights)

        this.setState({
            syscall_plot: {
                plot_type: "syscall",
                calls_per_second : {
                    x: cutout_x,
                    y: cutout_y,
                    name: 'Time series data'
                },
                index: this.state.index + 1
            },
            ids_plot: {
                plot_type: "ids",
                ids_score: {
                    x: cutout_x,
                    y: cutout_ids,
                    name: 'IDS score data',
                },
                index: this.state.index + 1,
                slider_threshold: this.state.slider.threshold 
            },
            original_data:{
                x: x,
                y: y,
                ids_score: ids_score
            },
            index: this.state.index + 1,
        });
    }
    
    handleRetrain = event => {
        //TODO Error message if User input is no number
        if (!isNaN(this.inputElement.value)){
            this.state.websocket.emit('training update', this.inputElement.value)
        }
    }
    
    addIncident = (data) => {
        this.incidentTable.current.updateTable(data.index, data.score)
    }
    
    automaticUserActions = (userAction) => {
        this.state.websocket.emit('user action', userAction)
    }

    componentDidMount(){
        let socket = io('ws://localhost:5000/');
        socket.on('connect', function() {
            console.log('Connected.')
            this.setState({
                websocket: socket
            });
        }.bind(this));

        //if recieved message stats update plot
        socket.on('stats', function(data) {
            this.setState({
                data : data
            });
            this.preparePlotData(data)
            //this.idsPlot.current.updatePlot(data)
            this.trainingInfo.current.update_training_info(data['ids_info'])
            //update syscallsistribution
            this.updateSyscallDistribution(data)
            //Add incident to  table if alarm state of ids plot is reached
            // -> depends on set threshold in plot
            if (this.state.alarm === 1){
                this.incidentTable.current.add_incident(data['time'], data['ids_info']['score'])
            }
        }.bind(this));
        //if recieved message user action update count of active users 
        socket.on('user action', function(data) {
            this.userAction.current.updateCount(data)
        }.bind(this));
    }
    
    render() {
        return(
            <div className="App">
              <div className="main">
              <header className="App-header">
                <h2>Anomaly Detection</h2>
              </header>
                <div className="dashboard">
                    <div className="item-plot">
                        <IDSPlot className="syscall-plot" 
                            plot_info={this.state.syscall_plot}  
                        />
                    </div>
                    <div className="item">
                        <TrafficLight className="traffic-light" ref={this.trafficLight}/>
                    </div>
                    <div className="item-plot">
                        <IDSPlot className="ids-plot" 
                            plot_info={this.state.ids_plot}  
                        />
                    </div>
                    <div className="item-status">
                        <TrainingInfo ref={this.trainingInfo} />
                    </div>
                    <div className="item">
                        <div className="info">
                                <UserInput className="training-input" inputRef={el => (this.inputElement = el)} />
                                <button className="button-basic" onClick={this.handleRetrain}>Retrain IDS</button>
                        </div>
                    </div>
                    <div className="item">
                        <div className="slider-text"> 
                            Incident threshold:  {this.state.slider.threshold}
                            <Slider
                              styles={{
                                  active: {
                                      backgroundColor: highlight1_color 
                                  },
                                  track: {
                                    backgroundColor: highlight_color
                                  },
                                  thumb: {
                                    backgroundColor: background_color,
                                    width: 25,
                                    height: 25
                                  }
                              }}
                              axis="x"
                              x={this.state.slider.threshold}
                              xmin={0}
                              xmax={1}
                              xstep={0.01}
                              onChange={({ x }) => this.setState({slider : {
                                  threshold: x.toFixed(2)
                              }})}
                            />
                        </div>
                    </div>
                    <div className="item">
                        <UserActionInput 
                            onChildClick={this.automaticUserActions} 
                            ref={this.userAction}
                        />
                    </div>
                    <div className="item-plot">
                        <SyscallTypePlot
                            ref={this.syscallDistPlot} 
                        />
                    </div>
                    <div className="item">
                        <IncidentTable className="incident-table" ref={this.incidentTable} />
                    </div>
                </div>
              </div>
        <footer className="footer">
            <p> License ... </p>
        </footer>

        </div>
        );
    };
}
export default App;
