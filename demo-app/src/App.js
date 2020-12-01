import React from 'react';
import io from 'socket.io-client';
import Slider from 'react-input-slider';
import './css/App.css';

import SyscallPlot from './SyscallPlot';
import IDSPlot from './IDSPlot';
import TrainingInfo from './TrainingInfo';
import IncidentTable from './Table'
import IDSSettings from './IDSSettings'
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
                stide: false,
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
                    y_2: [],
                    name: '',
                    alarm: 0
                },
                slider_threshold: IDS_THRESHOLD,
                multiple_active: false
            },
            original_data:{
                x: [],
                y: [],
                ids_score: [],
                ids_score_2: []
            },
            slider: {
                threshold: IDS_THRESHOLD
            },
            alarm: 0,
            alarm_of: '',
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

    handleSaveModel = (model) => {
        this.state.websocket.emit('save model', model)
    }
    
    handleLoadModel = (model) => {
        this.state.websocket.emit('load model', model)
    }

    handleStopModel = (model) => {
        console.log(model)
        this.state.websocket.emit('stop model', model)
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
        calc moving window for syscall 
        fill with leading zeros if needed
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
        cutout_x = this.adjustTimeArray(cutout_x)
        cutout_y = this.fillWithLeadingZeros(cutout_y)
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
                ids_score: this.state.original_data.ids_score,
                ids_score_2: this.state.original_data.ids_score_2
            }
        })
    }

    /*
        prepare plot data
        calc moving window for syscall 
        fill with leading zeros if needed
    */
    prepareIDSPlot = (time, ids_info) => {
        let multiple = ids_info['stide']['active'] && ids_info['mlp']['active']?true:false
        let x = this.state.original_data.x
        var cutout_ids = []
        var cutout_x = x.slice(Math.max(x.length - PLOT_WINDOW_CUTOUT, 1))
        cutout_x = this.adjustTimeArray(cutout_x)
        // check which IDS is active 
        if(ids_info['stide']['active'] && !multiple){
            let ids_score = this.state.original_data.ids_score
            ids_score.push(ids_info['stide']['score'])
            cutout_ids = ids_score.slice(Math.max(ids_score.length - PLOT_WINDOW_CUTOUT, 1))
            cutout_ids = this.fillWithLeadingZeros(cutout_ids)
            this.setState({
                ids_plot: {
                    type: 'stide',
                    ids_score : {
                        y: cutout_ids,
                        x: cutout_x,
                        name: 'IDS score data',
                        alarm: this.state.alarm
                    },
                    multiple_active: multiple
                },
                index: this.state.index + 1
            })
        }
        else if(ids_info['mlp']['active'] && !multiple){
            let ids_score = this.state.original_data.ids_score_2
            ids_score.push(ids_info['mlp']['score'])
            cutout_ids = ids_score.slice(
                Math.max(
                    ids_score.length - PLOT_WINDOW_CUTOUT, 1
                )
            )
            cutout_ids = this.fillWithLeadingZeros(cutout_ids)
            this.setState({
                ids_plot: {
                    type: 'mlp',
                    ids_score : {
                        x: cutout_x,
                        y_2: cutout_ids,
                        name: 'IDS score data',
                        alarm: this.state.alarm
                    },
                    multiple_active: multiple
                },
                index: this.state.index + 1
            })
        }
        else if(multiple){
            //stide 
            var cutout_stide = []
            let stide_score = this.state.original_data.ids_score
            stide_score.push(ids_info['stide']['score'])
            cutout_stide = stide_score.slice(Math.max(stide_score.length - PLOT_WINDOW_CUTOUT, 1))
            cutout_stide = this.fillWithLeadingZeros(cutout_stide)
            //mlp
            var cutout_mlp = []
            let mlp_score = this.state.original_data.ids_score_2
            mlp_score.push(ids_info['mlp']['score'])
            cutout_mlp = mlp_score.slice(Math.max(mlp_score.length - PLOT_WINDOW_CUTOUT, 1))
            cutout_mlp = this.fillWithLeadingZeros(cutout_mlp)
            //TODO multiple error
            this.setState({
                ids_plot: {
                    type: 'multiple',
                    ids_score : {
                        y: cutout_stide,
                        y_2: cutout_mlp,
                        x: cutout_x,
                        name: 'IDS score data',
                        alarm: this.state.alarm
                    },
                    multiple_active: multiple
                },
                index: this.state.index + 1
            })
        }
    }

    fillWithLeadingZeros = (data) => {
        let zeros = new Array(PLOT_WINDOW_CUTOUT - data.length).fill(0)
        return zeros.concat(data)
    }

    //adjust time array, so it starts at x=0 if no data was collected before
    adjustTimeArray = (data) => {
        let reverse_count = new Array(PLOT_WINDOW_CUTOUT - data.length).fill(0)
        var i
        if(data.length !== 0){
            let counter = 1
            for (i = PLOT_WINDOW_CUTOUT - data.length; i > 0; i-- ){
                reverse_count[i-1] = data[0] - counter 
                counter = counter + 1
            }
            return reverse_count.concat(data)
        }
        else {
            for (i = PLOT_WINDOW_CUTOUT - data.length; i > 0; i-- ){
                reverse_count[i-1] = -(i-1)
            }
            return reverse_count
        }
    }

    handleIDSSetting = (type, chosenIDS, training_size) => {
        //User can activate IDS through retrain or loading of model
        //info of which IDS and training_size if saved
        if(type === 'retrain'){
            let info = {
                type : chosenIDS,
                training_size : training_size 
            }
            if (chosenIDS === 'Stide'){
                this.setState({
                    active_ids : {
                        stide: true,
                        mlp: this.state.active_ids['mlp']
                    }
                })
            }
            else if (chosenIDS === 'MLP'){
                this.setState({
                    active_ids : {
                        stide: this.state.active_ids['stide'],
                        mlp: true
                    }
                })
            }
            this.state.websocket.emit('retrain', info)
        }
        else if(type === 'save'){
            this.handleSaveModel(chosenIDS)
        }
        else if(type === 'load'){
            if (chosenIDS === 'Stide'){
                this.setState({
                    active_ids : {
                        stide: true,
                        mlp: this.state.active_ids['mlp']
                    }
                })
            }
            else if (chosenIDS === 'MLP'){
                this.setState({
                    active_ids : {
                        stide: this.state.active_ids['stide'],
                        mlp: true
                    }
                })
            }
            this.handleLoadModel(chosenIDS)
        }
        else if(type === 'stop'){
            if (chosenIDS === 'Stide'){
                this.setState({
                    active_ids : {
                        stide: false,
                        mlp: this.state.active_ids['mlp']
                    }
                })
            }
            else if (chosenIDS === 'MLP'){
                this.setState({
                    active_ids : {
                        stide: this.state.active_ids['stide'],
                        mlp: false
                    }
                })
            }
            this.handleStopModel(chosenIDS)
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

    updateTrafficLight = (state_mlp, score_mlp, state_stide, score_stide) => {
        var lights = []
        //if still in training set light to yellow
        if (state_mlp === 0 && state_stide === 0){
            lights = [false, true, false]
            this.setState({alarm: 0})
        }
        else if (state_mlp === undefined && state_stide === 0){
            lights = [false, true, false]
            this.setState({alarm: 0})
        }
        else if (state_mlp === 0 && state_stide === undefined){
            lights = [false, true, false]
            this.setState({alarm: 0})
        }
        else if (state_mlp === undefined && state_stide === undefined){
            lights = [false, false, false]
            this.setState({alarm: 0})
        }
        // when alarm triggered
        //  update traffic light
        //  set alarm state
        else if (score_mlp > this.state.slider.threshold){
            lights = [true, false, false]
            this.setState({
                alarm: 1,
                alarm_of: 'mlp'
            })
        }
        else if (score_stide > this.state.slider.threshold){
            lights = [true, false, false]
            this.setState({
                alarm: 1,
                alarm_of: 'stide'
            })
        }
        else {
            lights = [false, false, true]
            this.setState({
                alarm: 0,
                alarm_of: ''
            })
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
            //set active ids
            //console.log(data)
            this.setState({
                data : data,
                active_ids: {
                    'stide': data['ids_info']['stide']['active'],
                    'mlp': data['ids_info']['mlp']['active']
                }
            });
            //update plot data 
            this.prepareSysPlot(
                data['time'], 
                data['syscall_info'])
            this.prepareIDSPlot(
                data['time'], 
                data['ids_info']
            )
            if(this.state.active_ids['stide']){
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
                // update ngram piechart
                this.updateNgramPlot(
                    data['ids_info']['stide']['top_ngrams'])
                //update table of converted syscalls to int (of ids) 
                this.intToSysTable.current.update_list(
                    data['ids_info']['stide']['int_to_sys'])
            }
            if(this.state.active_ids['mlp']){
                if(!this.state.ids_plot.multiple_active){
                    this.trainingInfo.current.update_training_info(
                        "mlp",
                        data['ids_info']['mlp']['state']
                    )
                }
            }
            this.updateTrafficLight(
                data['ids_info']['mlp']['state'],
                data['ids_info']['mlp']['score'],
                data['ids_info']['stide']['state'],
                data['ids_info']['stide']['score']
            )
            //update syscall distribution
            this.updateSyscallDistribution(
                data['syscall_info']['distribution_all']['sorted_syscalls'])
            // update useraction Info
            this.userAction.current.updateCount(
                data['userAction'])
            //Add incident to  table if alarm state of ids plot is reached
            // -> depends on set threshold in plot
            var key
            if (this.state.alarm === 1){
                if (this.state.active_ids['stide']){
                    key = "stide"
                }
                else {
                    key = "mlp"
                }
                console.log(data['analysis'])
                if (data['analysis']['alarm_content'].length > 0) {
                    this.incidentTable.current.add_incident(
                        data['time'], 
                        data['ids_info'][key]['score'], 
                        data['analysis']['alarm_content'],
                        key)
                }
            }
        }.bind(this));

        socket.on('enum', function(data) {
            this.attackInput.current.updateEnum(false)
        }.bind(this));

        socket.on('start', function(data) {
            window.location.reload();
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
                            type={this.state.ids_plot.type}
                            time={this.state.ids_plot.ids_score.x}
                            score={this.state.ids_plot.ids_score.y}
                            score2={this.state.ids_plot.ids_score.y_2}
                            alarm={this.state.alarm}
                            alarm_of={this.state.alarm_of}
                            threshold={this.state.slider.threshold}
                            index={this.state.index}
                            multiple_active={this.state.ids_plot.multiple_active}
                             
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
                                <IDSSettings className="training-input"
                                    onChildClick={this.handleIDSSetting}
                                />
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



