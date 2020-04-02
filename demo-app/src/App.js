import React from 'react';
import io from 'socket.io-client';
import './css/App.css';

import IDSPlot from './IDSPlot';
import TrainingInfo from './TrainingInfo';
import IncidentTable from './Table';
import UserInput from './UserInput'
import UserActionInput from './UserActionInput'

class App extends React.PureComponent{

    constructor(props){
        super(props)
        this.state = {
            websocket:0,
            data:[]
        }
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
    
    render() {
        return(
            <div className="App">
              <header className="App-header">
                <IDSPlot 
                    ref={this.idsPlot}  
                    addIncidentCallback={this.addIncident} 
                />
                <div className="nested">
                    <div>
                        <TrainingInfo ref={this.trainingInfo} />
                        <UserInput className="training-input" inputRef={el => (this.inputElement = el)} />
                        <button className="button-basic" onClick={this.handleRetrain}>Retrain IDS</button>
                    </div>
                    <UserActionInput 
                        onChildClick={this.automaticUserActions} 
                        ref={this.userAction}
                    />
                </div>
                <IncidentTable ref={this.incidentTable} />
              </header>
            </div>
        );
    };

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
            this.idsPlot.current.updatePlot(data)
            this.trainingInfo.current.update_training_info(data['ids_info'])
            //Add incident to  table if alarm state of ids plot is reached
            // -> depends on set threshold in plot
            if (this.idsPlot.current.state.alarm == 1){
                this.incidentTable.current.add_incident(data['time'], data['ids_info']['score'])
            }
        }.bind(this));
        //if recieved message user action update count of active users 
        socket.on('user action', function(data) {
            this.userAction.current.updateCount(data)
        }.bind(this));
    }
}

export default App;

