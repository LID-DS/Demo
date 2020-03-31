import React from 'react';
import io from 'socket.io-client';
import './css/App.css';

import IDSPlot from './IDSPlot';
import TrainingInfo from './TrainingInfo';
import IncidentTable from './Table';
import UserInput from './UserInput'

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
    
    render() {
        return(
            <div className="App">
              <header className="App-header">
                <IDSPlot ref={this.idsPlot} addIncidentCallback={this.addIncident} />
                <TrainingInfo ref={this.trainingInfo} />
                <UserInput inputRef={el => (this.inputElement = el)} />
                <button onClick={this.handleRetrain}>Retrain IDS</button>
                <div id="container"> </div>
                <IncidentTable ref={this.incidentTable} />
              </header>
            </div>
        );
    };

    componentDidMount(){
        //document.body.style.backgroundColor = '#ACB2B9'
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
            //send ids plot data (check if score falls below threshold value and set alarm state)
            this.idsPlot.current.updatePlot(data)
            this.trainingInfo.current.update_training_info(data['ids_info'])
            console.log(this.idsPlot.current.state.alarm)
            //Access alarm to check if incident happend 
            if (this.idsPlot.current.state.alarm == 1){
                this.incidentTable.current.add_incident(data['time'], data['ids_info']['score'])
            }
            else{
                console.log()
            }
        }.bind(this));
    }
}

export default App;

