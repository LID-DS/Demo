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
import PiePlot from './PiePlot';
import NgramTable from './NgramTable';

const IDS_THRESHOLD = 0.4
const PLOT_WINDOW_CUTOUT = 60

const highlight_color = '#f9f5d7'
const highlight1_color = '#470a0a'
const background_color = '#282828'

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
                    alarm: 0
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
                top: {},
            }
        }

        this.syscallDistPlot = React.createRef();
        this.trafficLight = React.createRef();
        this.idsPlot = React.createRef();
        this.trainingInfo = React.createRef();
        this.incidentTable = React.createRef();
        this.userAction = React.createRef();
        this.ngramTable = React.createRef();
        this.intToSysTable = React.createRef();
        this.ngramPlot = React.createRef();
    };
   
    //revceive info from TrainingInfo 
    handleTrainingChanged = (retrain_info) => {
        this.sendToBackend(retrain_info) 
    }
    
    //send info via websocket to backend 
    sendToBackend = (data) => {
       this.state.websocket.emit('training update', data) 
    }

    handleSaveModel = (data) => {
        this.state.websocket.emit('save model', null)
    }
    
    handleLoadModel = () => {
        this.state.websocket.emit('load model', null)
    }
    
    handleAttack = () => {
        this.state.websocket.emit('start attack', null)
    }

    handleTryHardAttack = () => {
        var info = "try hard" 
        this.state.websocket.emit('start attack', info)
    }

    handleEnum = () => {
        // send signal to start dirb enumeration
        this.state.websocket.emit('enum', null) 
    }
    
    updateSyscallDistribution = (data) => {
        // create list top of dictionaries 
        // each entry is name of systemcall and count of occurences
        let top = [];
        var i;
        try {
            for (i = 0; i < 5; i++){
                top.push(data['syscall_type_dict']['sorted_syscalls'][i]);
            }
            var sum_others = 0
            for (i = 5; i < data['syscall_type_dict']['sorted_syscalls'].length; i++){
                let tmp = Object.values(data['syscall_type_dict']['sorted_syscalls'][i])
                sum_others += tmp[0]
            }
            let others = {
                "others": sum_others
            }
            top.push(others) 
            //console.log(data['syscall_type_dict']['sorted_syscalls'])
            this.syscallDistPlot.current.handleValues(top)
        }
        catch (e) {
            //No syscalls received jet
        }
    }

    updateNgramPlot = (data) => {
        // create dict of ngrams for piechart 
        //console.log(data['ids_info']['top_ngrams'][0]) 
        var ngram_data = data['ids_info']['top_ngrams']
        var i
        for(i=0; i<ngram_data.length; i++) {
            //ngram_data[i][0] = ngram_data[i][0].toString()
            var tmp1 = ngram_data[i][0].toString()
            var tmp2 = ngram_data[i][1]
            ngram_data[i] = {[tmp1]: tmp2}
        }
        this.ngramPlot.current.handleValues(ngram_data)
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
        var current_score = data['ids_info']['score']

        //if still in training set light to yellow
        if(data['ids_info']['state'] === 0){
            lights = [false,true,false]
            this.setState({alarm: 0})
        }
        //when alarm triggered
        // update traffic light
        // set alarm state so App.js can access it
        else if(current_score > this.state.slider.threshold){
            lights = [true,false,false]
            this.setState({alarm: 1})
        }
        else {
            lights = [false,false,true]
            this.setState({alarm: 0})
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
                    alarm: this.state.alarm
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
            //update plot data 
            this.preparePlotData(data)
            //update training info 
            this.trainingInfo.current.update_training_info(data['ids_info'])
            //update syscall distribution
            this.updateSyscallDistribution(data)
            // update ngram table 
            this.ngramTable.current.update_list(data['ids_info']['top_ngrams'])
            // update ngram piechart
            this.updateNgramPlot(data)
            //update table of converted syscalls to int (of ids) 
            this.intToSysTable.current.update_list(data['ids_info']['int_to_sys'])

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
                        <div className="slider"> 
                            <div>Incident threshold:  {this.state.slider.threshold}</div>
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
                    <div className="item-plot">
                        <IDSPlot className="ids-plot" 
                            plot_info={this.state.ids_plot}  
                        />
                    </div>
                    <div className="item">
                        <UserActionInput 
                            onChildClick={this.automaticUserActions} 
                            ref={this.userAction}
                        />
                    </div>
                    <div className="item">
                        <TrainingInfo ref={this.trainingInfo} />
                    </div>
                    <div className="item">
                        <div className="info">
                                <UserInput className="training-input" 
                                    inputRef={el => (this.inputElement = el)} />
                                <button className="button-basic" 
                                    onClick={this.handleRetrain}>
                                    Retrain IDS-Model
                                </button>
                                <div>
                                    <button className="button-basic" 
                                        onClick={this.handleSaveModel}>
                                        Save Trained IDS-Model
                                    </button>
                                    <button className="button-basic" 
                                        onClick={this.handleLoadModel}>
                                        Load Trained IDS-Model
                                    </button>
                                </div>
                        </div>
                    </div>
                    <div className="item-plot">
                        <div className="title">
                            System Call Distribution
                        </div>
                        <PiePlot
                            info={"syscalldist"}
                            ref={this.syscallDistPlot} 
                        />
                    </div>
                    <div className="item">
                        <IncidentTable className="incident-table" ref={this.incidentTable} />
                    </div>
                    <div className="item-plot">
                        <div className="title">
                            Ngram Distribution
                        </div>
                        <PiePlot
                            info={"ngram"}
                            conversionTable={this.state.data["ids_info"]}
                            ref={this.ngramPlot} 
                        />
                    </div>
                    <div className="item">
                        <div className="title">
                            Reconnaissance:{"\n"}
                        </div>
                        <button className="button-basic" 
                            onClick={this.handleEnum}>
                            Launch Dirb Enum 
                        </button>
                        <div className="title">
                            Attacks:{"\n"}
                        </div>
                        <button className="button-basic" 
                            onClick={this.handleAttack}>
                            SQL Injection
                        </button>
                        <button className="button-basic" 
                            onClick={this.handleTryHardAttack}>
                            Try Hard SQL Injection
                        </button>
                    </div>
                    <div className="item">
                        <NgramTable className="ngram-table" ref={this.intToSysTable}/>
                    </div>
                    <div className="item">
                        <div className="title">
                            Ngrams in normal mode
                        </div>
                        <NgramTable className="ngram-table" ref={this.ngramTable}/>
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
