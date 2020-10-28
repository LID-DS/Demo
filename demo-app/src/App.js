import React from 'react';
import io from 'socket.io-client';
import Slider from 'react-input-slider';
import './css/App.css';

import SyscallPlot from './SyscallPlot';
import IDSPlot from './IDSPlot';
import TrainingInfo from './TrainingInfo';
import IncidentTable from './Table_alt'
import UserInput from './UserInput'
import UserActionInput from './UserActionInput'
import TrafficLight from './TrafficLight';
import PiePlot from './PiePlot';
import NgramTable from './NgramTable';
import logo from './images/ScaDS_AI_Logo.png'
import AttackInput from './AttackInput'

const IDS_THRESHOLD = 0.05
const PLOT_WINDOW_CUTOUT = 60

const highlight_color = '#f9f5d7'
const highlight1_color = '#470a0a'
const background_color = '#282828'

class App extends React.PureComponent{

    constructor(props){
        super(props)
        this.state = {
            index: 0,
            websocket:0,
            data:[],
            active_ids: { 
                stide: true,
                mlp: false
            },
            syscall_plot: {
                type: "syscall plot",
                calls_per_second : {
                    y: [],
                    x: [],
                    name: ''
                },
            },
            ids_plot: {
                type: "stide",
                ids_score: {
                    x: [], 
                    y: [],
                    name: '',
                    alarm: 0
                },
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
            syscall_type_dist: {
                complete: {} ,
                top: {},
            },
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
        this.attackInput = React.createRef();

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
    
    handleAttackInput = (form, specify) => {
        this.state.websocket.emit(form, specify)
    }
    
    updateSyscallDistribution = (sorted_syscalls) => {
        // create list top of dictionaries 
        // each entry is name of systemcall and count of occurences
        let top = [];
        var i;
        try {
            for (i = 0; i < 5; i++){
                top.push(sorted_syscalls[i]);
            }
            var sum_others = 0
            for (i = 5; i < sorted_syscalls.length; i++){
                let tmp = Object.values(sorted_syscalls[i])
                sum_others += tmp[0]
            }
            let others = {
                "others": sum_others
            }
            top.push(others) 
            this.syscallDistPlot.current.handleValues(top)
        }
        catch (e) {
            //No syscalls received jet
        }
    }

    updateNgramPlot = (ngram_data) => {
        // create dict of ngrams for piechart 
        //console.log(data['ids_info']['top_ngrams'][0]) 
        //var ngram_data = data['ids_info']['stide']['top_ngrams']
        var i
        if (typeof ngram_data === 'object'){
            for(i=0; i<ngram_data.length; i++) {
                //ngram_data[i][0] = ngram_data[i][0].toString()
                var tmp1 = ngram_data[i][0].toString()
                var tmp2 = ngram_data[i][1]
                ngram_data[i] = {[tmp1]: tmp2}
            }
            this.ngramPlot.current.handleValues(ngram_data)
        }
    }

    /*
        prepare plot data
        calc moving window for syscall and ids plot
        show correct trafficlight
    */
    prepareSysPlot = (time, syscall_data) => {
        // handle system call information
        // get old time information
        let x = this.state.original_data.x
        //get old count of syscalls 
        let y = this.state.original_data.y
        //add newest entry
        x.push(time)
        y.push(syscall_data['sum_second'])
        //prepare cutout to plot correct window
        // only show static window of PLOT_WINDOW_CUTOUT seconds
        // select only last entries of original data for cutout window
        var cutout_x = 0
        var cutout_y = 0
        cutout_x = x.slice(Math.max(x.length - PLOT_WINDOW_CUTOUT, 1))
        cutout_y = y.slice(Math.max(y.length - PLOT_WINDOW_CUTOUT, 1))
        this.setState({
            syscall_plot: {
                type: "syscall plot",
                calls_per_second : {
                    x: cutout_x,
                    y: cutout_y,
                    name: 'Time series data'
                }
            },
            original_data: {
                x: x,
                y: y,
                ids_score: this.state.original_data.ids_score
            }
        })
    }

    prepareIDSPlot = (time, ids_info) => {
        let ids_score = this.state.original_data.ids_score
        let x = this.state.original_data.x
        ids_score.push(ids_info['score'])
        var cutout_x = x.slice(Math.max(x.length - PLOT_WINDOW_CUTOUT, 1))
        var cutout_ids = ids_score.slice(Math.max(ids_score.length - PLOT_WINDOW_CUTOUT, 1))
        cutout_ids = ids_score.slice(Math.max(ids_score.length - PLOT_WINDOW_CUTOUT, 1))
        this.setState({
            ids_plot: {
                type: "stide",
                ids_score : {
                    y: cutout_ids,
                    x: cutout_x,
                    name: 'IDS score data',
                    alarm: this.state.alarm
                }
            },
            index: this.state.index + 1
        })
    }
    
    handleRetrain = event => {
        //TODO Error message if User input is no number
        if (!isNaN(this.inputElement.value)){
            this.state.websocket.emit('training update', this.inputElement.value)
        }
    }

    IDSChooser = (active_ids) => {
        // [stide, mlp]
        this.setState({
            active_ids: {
                stide: active_ids[0],
                mlp: active_ids[1]
            }
        })
        console.log(active_ids)
        this.state.websocket.emit(
            'choosing ids', {
                "stide":active_ids[0], 
                "mlp": active_ids[1]
            }
        )
    }
    
    automaticUserActions = (userAction) => {
        this.state.websocket.emit('user action', userAction)
    }

    updateTrafficLight = (state, score) => {
        var lights = []
        //if still in training set light to yellow
        if (state == 0){
            lights = [false, true, false]
            this.setState({alarm: 0})
        }
        // when alarm triggered
        //  update traffic light
        //  set alarm state
        else if (score > this.state.slider.threshold){
            lights = [true, false, false]
            this.setState({alarm: 1})
        }
        else {
            lights = [false, false, true]
            this.setState({alarm: 0})
        }
        this.trafficLight.current.updateLight(lights)
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
            //check for alarm
            //update plot data 
            this.prepareSysPlot(data['time'], data['syscall_info'])
            if(this.state.active_ids['stide']){
                this.updateTrafficLight(
                    data['ids_info']['stide']['state'],
                    data['ids_info']['stide']['score']
                )
                this.prepareIDSPlot(
                    data['time'], 
                    data['ids_info']['stide'])
                // update ngram table if stide is active
                this.ngramTable.current.update_list(
                    data['ids_info']['stide']['top_ngrams'])
                //update training info 
                this.trainingInfo.current.update_training_info(
                    "stide",
                    data['ids_info']['stide']['state'],
                    data['ids_info']['stide']['current_ngrams'],
                    data['ids_info']['stide']['training_size']
                )
            }
            //update syscall distribution
            this.updateSyscallDistribution(
                data['syscall_info']['distribution_all']['sorted_syscalls'])
            // update ngram piechart
            this.updateNgramPlot(
                data['ids_info']['stide']['top_ngrams'])
            //update table of converted syscalls to int (of ids) 
            this.intToSysTable.current.update_list(
                data['ids_info']['stide']['int_to_sys'])
            // update useraction Info
            this.userAction.current.updateCount(
                data['userAction'])
            //Add incident to  table if alarm state of ids plot is reached
            // -> depends on set threshold in plot
            if (this.state.alarm === 1){
                if (this.state.active_ids['stide']){
                    var key = "stide"
                }
                else {
                    var key = "mlp"
                }
               if (data['ids_info'][key]['alarm_content'].length > 0) {
                    this.incidentTable.current.add_incident(
                        data['time'], 
                        data['ids_info'][key]['score'], 
                        data['ids_info'][key]['alarm_content'])
                }
            }
        }.bind(this));

        socket.on('enum', function(data) {
            this.attackInput.current.updateEnum(false)
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
                        <SyscallPlot className="syscall-plot"
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
                              xmax={0.2}
                              xstep={0.005}
                              onChange={({ x }) => this.setState({slider : {
                                  threshold: x.toFixed(3)
                              }})}
                            />
                        </div>
                    </div>
                    <div className="item-plot">
                        <IDSPlot className="ids-plot"
                            time={this.state.ids_plot.ids_score.x}
                            score={this.state.ids_plot.ids_score.y}
                            alarm={this.state.alarm}
                            threshold={this.state.slider.threshold}
                            index={this.state.index}
                        />
                    </div>
                    <div className="item">
                        <UserActionInput 
                            onChildClick={this.automaticUserActions} 
                            ref={this.userAction}
                        />
                    </div>
                    <div className="item">
                        <TrainingInfo 
                            onChildClick={this.IDSChooser}
                            ref={this.trainingInfo} />
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
                            Live System Call Distribution
                        </div>
                        <PiePlot
                            info={"syscalldist"}
                            ref={this.syscallDistPlot} 
                        />
                    </div>
                    <div className="item">
                        <div>
                        <IncidentTable 
                            className="incident-table" 
                            ref={this.incidentTable} />
                        </div>
                    </div>
                    <div className="item-plot">
                        <div className="title">
                            Training Ngram Distribution
                        </div>
                        <PiePlot
                            info={"ngram"}
                            conversionTable={this.state.data["ids_info"]}
                            ref={this.ngramPlot} 
                        />
                    </div>
                    <div className="item">
                        <AttackInput 
                            onChildClick={this.handleAttackInput} 
                            ref={this.attackInput}
                        />
                    </div>
                    <div className="item">
                        <NgramTable 
                            className="ngram-table" 
                            ref={this.intToSysTable}/>
                    </div>
                    <div className="item">
                        <div className="title">
                            Ngrams in normal mode
                        </div>
                        <NgramTable 
                            className="ngram-table" 
                            ref={this.ngramTable}/>
                    </div>
                </div>
                    
              </div>
        <footer className="footer">
            <a href="https://www.scads.de/en/">
             <img src={logo} alt="ScaDS AI Logo"/>
            </a>
        </footer>

        </div>
        );
    };
}


export default App;



